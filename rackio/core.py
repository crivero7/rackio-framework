# -*- coding: utf-8 -*-
"""rackio/core.py

This module implements the core app class and methods for Rackio.
"""

import logging
import concurrent.futures

import falcon

from peewee import SqliteDatabase, MySQLDatabase, PostgresqlDatabase

from ._singleton import Singleton
from .logger import LoggerEngine
from .controls import ControlManager
from .alarms import AlarmManager
from .state import StateMachineManager
from .workers import LoggerWorker, ControlWorker, AlarmWorker, APIWorker, _ContinousWorker
from .api import TagResource, TagCollectionResource, TagHistoryResource, TrendResource, AlarmResource, AlarmCollectionResource, EventCollectionResource

from .dbmodels import SQLITE, MYSQL, POSTGRESQL


class Rackio(Singleton):

    """Rackio main application class.

    This class is a singleton by inheritance, this makes
    it available in each module of an end application or
    code project

    # Example
    
    ```python
    >>> from rackio import Rackio
    >>> app = Rackio()
    ```

    """

    def __init__(self, context=None):

        super(Rackio, self).__init__()
        
        self._context = context

        self._logging_level = logging.INFO
        self._log_file = ""

        self._worker_functions = list()
        self._continous_functions = list()
        self._custom_observer = None
        self._control_manager = ControlManager()
        self._alarm_manager = AlarmManager()
        self._machine_manager = StateMachineManager()
        
        self.db = None
        self._db_manager = LoggerEngine()

        self._api = falcon.API()

        _tag = TagResource()
        _tags = TagCollectionResource()
        _tag_history = TagHistoryResource()
        _tag_trend = TrendResource()
        _alarm = AlarmResource()
        _alarms = AlarmCollectionResource()
        _events = EventCollectionResource()

        self._api.add_route('/api/tags/{tag_id}', _tag)
        self._api.add_route('/api/tags', _tags)

        self._api.add_route('/api/tags/history/{tag_id}', _tag_history)
        self._api.add_route('/api/tags/trends/{tag_id}', _tag_trend)

        self._api.add_route('/api/alarms/{alarm_name}', _alarm)
        self._api.add_route('/api/alarms', _alarms)

        self._api.add_route('/api/events', _events)

    def set_log(self, level=logging.INFO, file=""):
        """Sets the log file and level.
        
        # Parameters
        level (str): logging.LEVEL.
        file (str): filename to log.
        """

        self._logging_level = level
        
        if file:
            self._log_file = file

    def set_db(self, dbfile=':memory:', dbtype=SQLITE, **kwargs):
        """Sets the database file.
        
        # Parameters
        dbfile (str): a path to database file.
        """

        from .dbmodels import proxy

        if dbtype == SQLITE:
            
            self._db = SqliteDatabase(dbfile, pragmas={
                'journal_mode': 'wal',
                'cache_size': -1 * 64000,  # 64MB
                'foreign_keys': 1,
                'ignore_check_constraints': 0,
                'synchronous': 0}
            )

        elif dbtype == MYSQL:
            
            app = kwargs['app']
            self._db = MySQLDatabase(app, **kwargs)

        elif dbtype == POSTGRESQL:
            
            app = kwargs['app']
            self._db = PostgresqlDatabase(app, **kwargs)
        
        proxy.initialize(self._db)
        self._db_manager.set_db(self._db)

    def set_dbtags(self, tags, period=0.5):
        """Sets the database tags for logging.
        
        # Parameters
        tags (list): A list of the tags.
        """

        self._db_manager.set_period(period)
        
        for _tag in  tags:
            self._db_manager.add_tag(_tag)

    def append_rule(self, rule):
        """Append a rule to the control manager.
        
        # Parameters
        rule (Rule): a rule object.
        """

        self._control_manager.append_rule(rule)

    def append_control(self, control):
        """Append a control to the control manager.
        
        # Parameters
        control (Control): a control object.
        """

        self._control_manager.append_control(control)

    def append_alarm(self, alarm):
        """Append an alarm to the alarm manager.
        
        # Parameters
        alarm (Alarm): an alarm object.
        """

        self._alarm_manager.append_alarm(alarm)

    def append_machine(self, machine):
        """Append a state machine to the state machine manager.
        
        # Parameters
        machine (StateMachine): a state machine object.
        """

        self._machine_manager.append_machine(machine)

    def add_route(self, route, resource):
        """Append a resource and route the api.
        
        # Parameters
        route (str): The url route for this resource.
        resource (object): a url resouce template class instance.
        """

        self._api.add_route(route, resource)

    def rackit(self, period):
        """Decorator method to register functions plugins.
        
        This method will register into the Rackio application
        a new function to be executed by the Thread Pool Executor

        # Example
    
        ```python
        @app.rackit
        def hello():
            print("Hello!!!")
        ```

        # Parameters
        period (float): Value of the default loop execution time.
        """

        def decorator(f):

            def wrapper():
                try:
                    f()
                except Exception as e:
                    error = str(e)
                    print("{}:{}".format(f.__name__, error))

            # _worker_function = (f, period)
            _worker_function = (wrapper, period)
            self._worker_functions.append(_worker_function)
            return f
        
        return decorator

    def rackit_on(self, function=None, worker_name=None, period=0.5, pause_tag=None, stop_tag=None):
        """Decorator method to register functions plugins with continous execution.
        
        This method will register into the Rackio application
        a new function to be executed by the Thread Pool Executor

        # Example
    
        ```python
        @app.rackit_on(period=0.5)
        def hello():
            print("Hello!!!")

        @app.rackit_on
        def hello_world():
            print("Hello World!!!")
        ```

        # Parameters
        period (float): Value of the default loop execution time, if period is not defined 0.5 seconds is used.
        """
    
        if function:
            return _ContinousWorker(function)
        else:
            def wrapper(function):
                return _ContinousWorker(function, worker_name, period, pause_tag, stop_tag)

            return wrapper

    def run(self, port=8000):

        """Runs the main execution for the application to start serving.
        
        This will put all the components of the application at run

        # Example
    
        ```python
        >>> app.run()
        ```
        """

        log_format = "%(asctime)s:%(levelname)s:%(message)s"

        if self._log_file:
            logging.basicConfig(filename=self._log_file, level=self._logging_level, format=log_format)
        else:
            logging.basicConfig(level=self._logging_level, format=log_format)

        _control_worker = ControlWorker(self._control_manager)
        _alarm_worker = AlarmWorker(self._alarm_manager)
        _api_worker = APIWorker(self._api, port)

        if self._db_manager:
            _db_worker = LoggerWorker(self._db_manager)
            _db_worker.start()
        
        _control_worker.start()
        _alarm_worker.start()
        _api_worker.start()

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            
            for _f, period in self._worker_functions:

                executor.submit(_f)

            for _f in self._continous_functions:

                executor.submit(_f)

        _control_worker.join()
        _alarm_worker.join()
        _api_worker.join()
            