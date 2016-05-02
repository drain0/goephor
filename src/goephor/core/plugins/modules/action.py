'''
Created on Apr 26, 2016

@author: iitow
'''
import importlib
import sys
from environment import EnvManager
import time


class Manager(object):
    ''' 
    This class manages state of action objects
    
    :note: This is passed into each of the plugins and can be used to manage
    Serveral states.
    '''
    def __init__(self, config, EnvManager,verbose=False,debug=False):
        '''
        Constructor
        
        :param config: nest dict from manifest
        :param EnvManager: Holds the state of the Environment
        :param verbose: set verbosity
        :param debug: set debug
        '''
        self.verbose = verbose
        self.debug = debug
        self.chain = []
        self.config = config
        self.EnvManager = EnvManager
        self.failure = False

    def to_obj(self, action, action_manager):
        ''' 
        Converts action dictionary to action obj
        
        :param action: base action dict
        :param action_manager: from chain.Run pass in Action_manager
        :note: We initialize the action_manager in chain.Run and pass
        the obj back to each Action Obj which gives the class full
        access to initialize nest actions and have access to environment.
        '''
        try:
            path = action.keys()[0]
            resolve_path = path.split('.')
            IMP = resolve_path[0]
            CLASS = resolve_path[1]
            definition = resolve_path[2]
            parameters = []
            defaults = {}
            for param in action.get(path):
                if isinstance(param, dict):
                    name = param.keys()[0]
                    value = param.get(name)
                    defaults[name] = value
                else:
                    parameters.append(param)
        except Exception as e:
            error = '[Error] [%s] %s' % (type(self).__name__,str(e))
            raise Exception(error)
        try:
            action_obj = Action(path,
                                IMP,
                                CLASS,
                                definition,
                                parameters,
                                defaults,
                                action_manager)
            return action_obj
        except Exception as e:
            error =  '[Error] [%s] %s' % (type(self).__name__,str(e))
            raise Exception(error)

    def add(self, action_obj):
        '''
        Append an action obj to chain
        
        :param action_obj: Obj
        '''
        self.chain.append(action_obj)

    def insert(self, index, action_obj):
        '''
        Insert action object at a given index in the chain
        
        :param index: Int of chain
        :param action_obj: Obj
        '''
        self.chain.insert(index, action_obj)

    def get_index(self, memory_address):
        '''
        Get the index number of an action object in the chain
        
        :param memory_address: String, of object.__repr__(self)
        :note: See plugins.condition for usage
        '''
        cnt = 1
        for action in self.chain:
            if str(memory_address) == str(action):
                return cnt
            cnt += 1
        return None


class Action(object):
    ''' 
    Object containing instructions to create and execute actions
    '''
    def __init__(self,
                 name,
                 IMP,
                 CLASS,
                 DEF,
                 parameters,
                 defaults,
                 action_manager):
        '''
        Constructor
        
        :param name: String, full resolve path
        :param IMP: String, import name
        :param CLASS: String, class name
        :param DEF: String, definition name
        :param parameters: list
        :param defaults: Dict
        :param action_manager: Obj
        '''
        self.name = name
        self.IMP = IMP
        self.CLASS = CLASS
        self.DEF = DEF
        self.EnvManager = EnvManager()
        self.parameters = self.EnvManager.sanitize(parameters)
        self.defaults = self.EnvManager.sanitize(defaults)
        self.ignore = False
        self.set_ignore()
        self.action_manager = action_manager
        self.instance = self._init_instance()
        self.duration = None
        self.session = None

    def __repr__(self):
        '''
        Override container name so we can match the array in the chain
        
        :note: This is how we match chain to current plugin using object.__repr__(self)
        '''
        return object.__repr__(self.instance)
    
    def set_ignore(self):
        '''
        catch the ignore parameter and delete it in defaults
        '''
        defaults = {}
        for key,value in self.defaults.iteritems():
            if key == 'ignore':
                if value:
                    self.ignore = True
            else:
                defaults[key]=value
        self.defaults = defaults
                

    def get_receipt(self):
        '''
        return a dictionary of all Action info
        '''
        return {"IMP": self.IMP,
                "CLASS": self.CLASS,
                "DEF": self.DEF,
                "parameters": self.parameters,
                "defaults": self.defaults,
                "duration": self.duration,
                "session": self.session}

    def pprint(self,title="",footer=""):
        ''' 
        print state about the object pretty
        
        :param title: String
        :param footer: String
        '''
        print "\n\n[%s]\n" % title
        print "%s %s" % ('[import]'.rjust(15), self.IMP)
        print "%s %s" % (' [class]'.rjust(15), self.CLASS)
        print "%s %s" % (' [funct]'.rjust(15), self.DEF)
        print '%s %s' % ('[duration]'.rjust(15), self.duration)
        print ""
        print "%s" % ('[parameters]'.rjust(15))
        for param in self.parameters:
            print "      %s" % (param.strip().ljust(20))
        print ""
        print "%s" % ('[defaults]'.rjust(15))
        for key, value in self.defaults.iteritems():
            print '%s: %s' % (key.rjust(10), value)
        print ""
        print "%s" % ('[session]'.rjust(15))
        print self.session
        print "\n[%s]\n" % footer
    
    def _init_instance(self):
        ''' Initializes the class
        :note: we initialize the plugin class so we can pass info into action Obj before run.
        '''
        IMP = 'goephor.core.plugins.%s' % (self.IMP)
        _module = importlib.import_module(IMP)
        CLASS = getattr(_module, self.CLASS)
        CLASS = CLASS(self.action_manager)
        return CLASS

    def execute(self):
        ''' execute the instruction
        '''
        DEF = getattr(self.instance, self.DEF)
        start = time.time()
        self.session = DEF(*self.parameters, **self.defaults)
        end = time.time()
        self.duration = end - start
        return self.session