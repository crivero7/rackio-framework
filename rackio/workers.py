# -*- coding: utf-8 -*-
"""rackio/workers.py

This module implements all thread classes for workers.
"""
import time
import logging
from threading import Thread
from wsgiref.simple_server import make_server

from .controls import ControlManager
from .engine import CVTEngine
from .dbmodels import TagTrend, TagValue, Event


class BaseWorker(Thread):

    def  __init__(self):

        super(BaseWorker, self).__init__()


class ThreadWorker(BaseWorker):

    def  __init__(self, worker_function, period):

        super(ThreadWorker, self).__init__()
        self._period = period
        self._worker_function = worker_function

    def run(self):

        while True:

            time.sleep(self._period)

            self._worker_function()


class ControlWorker(BaseWorker):

    def __init__(self, manager, period=0.1):

        super(ControlWorker, self).__init__()
        
        self._manager = manager
        self._period = period

        self._manager.attach_all()

    def run(self):

        if (not self._manager.rule_tags()) and (not self._manager.control_tags()):
            return

        _queue = self._manager._tag_queue

        while True:
            
            time.sleep(self._period)

            if not _queue.empty():
                item = _queue.get()
                
                _tag = item["tag"]

                self._manager.execute(_tag)


class AlarmWorker(BaseWorker):

    def __init__(self, manager, period=0.25):

        super(AlarmWorker, self).__init__()
        
        self._manager = manager
        self._period = period

        self._manager.attach_all()

    def run(self):

        if not self._manager.alarm_tags():
            return

        _queue = self._manager._tag_queue

        while True:
            
            time.sleep(self._period)

            if not _queue.empty():
                item = _queue.get()
                
                _tag = item["tag"]

                self._manager.execute(_tag)


class StateMachineWorker(BaseWorker):

    def __init__(self, manager, period=0.25):

        super(StateMachineWorker, self).__init__()
        
        self._manager = manager
        self._period = period

    def run(self):

        if not self._manager.get_machines():
            return

        def loop(machine):

            try:
                state_name = machine.current_state.name
                method_name = "while_" + state_name
                method = getattr(machine, method_name)
                
                method()

            except:
                logging.error("Machine has no method - {}".format(method_name))

        while True:
            
            time.sleep(self._period)

            for machine in self._manager.get_machines():
                
                loop(machine)


STOP = "Stop"
PAUSE = "Pause"
RUNNING = "Running"
ERROR = "Error"


class _ContinousWorker:

    def __init__(self, f, worker_name=None, period=0.5, pause_tag=None, stop_tag=None):

        self._f = f
        self._name = worker_name
        self._period = period
        self._pause_tag = pause_tag
        self._stop_tag = stop_tag
        self._status = STOP       # [STOP, PAUSE, RUNNING, ERROR]

        from .core import Rackio

        rackio = Rackio()
        rackio._continous_functions.append(self)

    def serialize(self):

        result = dict()
        result["name"] = self._name
        result["period"] = self._period
        result["pause_tag"] = self._pause_tag
        result["stop_tag"] = self._stop_tag
        result["status"] = self._status

        return result

    def pause(self):

        if self._pause_tag:
            _cvt = CVTEngine()
            _cvt.write_tag(self._pause_tag, True)

            return True

    def resume(self):

        if self._pause_tag:
            _cvt = CVTEngine()
            _cvt.write_tag(self._pause_tag, False)

            return True

    def stop(self):

        if self._stop_tag:
            _cvt = CVTEngine()
            _cvt.write_tag(self._stop_tag, True)

            return True

    def get_name(self):

        return self._name

    def get_status(self):

        return self._status
    
    def __call__(self, *args):

        _cvt = CVTEngine()

        time.sleep(self._period)

        while True:

            self._status = RUNNING

            now = time.time()

            if self._stop_tag:
                stop = _cvt.read_tag(self._stop_tag)

                if stop:
                    self._status = STOP
                    return

            if self._pause_tag:
                pause = _cvt.read_tag(self._pause_tag)
                
                if not pause:
                    
                    try:
                        self._f()
                    except Exception as e:
                        error = str(e)
                        logging.error("Worker - {}:{}".format(self._f.__name__, error))
                        self._status = ERROR

                else:
                    self._status = PAUSE

            else:
                try:
                    self._f()
                except Exception as e:
                    error = str(e)
                    logging.error("Worker - {}:{}".format(self._f.__name__, error))
                    self._status = ERROR

            elapsed = time.time() - now

            if elapsed < self._period:
                time.sleep(self._period - elapsed)
            else:
                logging.warning("Worker - {}: Unable to perform on time...".format(self._f.__name__))
            

class APIWorker(BaseWorker):

    def __init__(self, app, port=8000):

        super(APIWorker, self).__init__()

        self._api_app = app
        self._port = port

    def run(self):

        with make_server('', self._port, self._api_app) as httpd:
            logging.info('Serving on port {}...'.format(self._port))

            # Serve until process is killed
            httpd.serve_forever()


class LoggerWorker(BaseWorker):

    def __init__(self, manager):

        super(LoggerWorker, self).__init__()
        
        self._manager = manager
        self._period = manager.get_period()

    def run(self):

        tags = self._manager.get_tags()

        if not tags:
            return

        try:
            self._manager.drop_tables([TagTrend, TagValue, Event])
        except Exception as e:
            print(e)

        self._manager.create_tables([TagTrend, TagValue, Event])
        
        for tag in tags:

            self._manager.set_tag(tag)

        _cvt = CVTEngine()

        time.sleep(self._period)

        while True:

            now = time.time()

            for _tag in self._manager._logging_tags:
                value = _cvt.read_tag(_tag)
                self._manager.write_tag(_tag, value)
            
            elapsed = time.time() - now

            if elapsed < self._period:
                time.sleep(self._period - elapsed)
            else:
                logging.warning("Logger Worker: Failed to log on item...")
            