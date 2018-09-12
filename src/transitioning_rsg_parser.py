# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 10:08:17 2017

@author: rikhoekstra
"""
import os
import re
import logging
from dateparser import parse as dateparse
from transitions import Machine
from collections import Counter
p1 = re.compile('(\w*)([l\d]*[l\d]+)\s*(januari|februari|maart|april|mei|juni|juli|augustus|september|oktober|november|december)\s+([l\d]+)', re.I)
p2 = re.compile("(((?P<roman>\w*[A-Za-z]))*\s*((?P<rnr>\d{1,4}[\s\.]+)))(?P<resolutie>.*)")



class Session(object):
    """session model for RSG zittingsdagen"""
    def __init__(self, date=(''), resolutions={}):
        date = make_date(date)
        #print date
        self.date = date[1]
        self.rawdate = date[0]
        self.volgnr = 0
        self.resolutions = {}
        
    def set_resolution(self, resolution):
        number = self.volgnr
        self.resolutions[number] = resolution
        self.volgnr += 1
        
    def get_resolution(self, number):
        resolution = self.resolutions[number]
        setattr(resolution, self.date)
        
    def set_date(self, date=''):
        date = make_date(date)
        self.date = date[1]
        self.rawdate = date[0]
        
        
class Resolution(object):
    """resolution model for RSG decisions"""
    def __init__(self, text=''):
        self.text = [text]
        self.roman = ''
        self.nr = 0
        self.rawnr = ''
        self.footnote = False
        
    def get_resolution(self, sep='\n'):
        if isinstance(self.text, str):
            result = self.text
        else:
            result = sep.join(self.text or [])
        return result
    
    def mknr(self, pattern=p2):
        pat = pattern.search(self.get_resolution(sep=''))
#        import pdb; pdb.set_trace()
        if pat:
            if pat.groups() and len(pat.groups()) >1:
                try:
                    romannr = pat.groupdict().get('roman').strip()
                    self.roman = romannr
                except (AttributeError, ValueError) :
                    pass
                try:
                    nr = pat.groupdict().get('rnr').strip()
                    if nr.find('.'):
                        nr = nr[:nr.find('.')] # throw away all after the dot
                    self.nr = int(nr)
                except (ValueError, AttributeError):
                    pass
                self.rawnr = pat.groupdict().get('rnr')
#                f = self.text.find(self.rawnr)
                self.text = pat.groupdict().get('resolutie').strip()
        
    def __repr__(self):
        return self.get_resolution()


states = ['start',
          'presentie_state',
          'resolution_state',
          'element_state',
          'pn_state',
          'no_pn_state',
          'date_state',
          'new_session_state',
          'post_prandium_state'
          'new_resolution_state',
          'footnote_state',
          'resolution_continuation_state',
          'el_handled',
          'done'
          ]

transitions = [
    {'trigger':'d_page', 
     'source':'start', 
     'dest':'resolution_state',
     'conditions': 'page_state_transition',
     'prepare': 'prepare'},
     
    {'trigger':'divide', 
    'source':'resolution_state', 
    'dest':'element_state',
    'conditions': 'page_state_transition',
    'after':['pagenumber', 'divide_page_transition']},

#    {'trigger':'check_date',
#     'source':'element_state',
#     'dest': 'el_handled',
#     'unless': 'element_is_date',
#     },
     
     {'trigger':'check_date',
     'source':'element_state',
     'dest': 'el_handled',
     'after': ['make_session'],
     'conditions': 'element_is_date',
     },
          
     {'trigger':'check_resolution',
      'source': 'element_state',
      'dest': 'el_handled',
      'conditions':'element_is_resolution',
      'after': ['make_resolution'],}, 

    {'trigger':'check_cont_resolution',
      'source': 'element_state',
      'dest': 'el_handled',
      'conditions': 'element_is_c_res',
      'after': ['res_cont_transition'],},


    {'trigger':'check_footnote',
      'source': 'element_state',
      'dest': 'el_handled',
      'conditions': 'element_is_footnote',
      'after': ['make_resolution', 'footnote_transition'],},

    {'trigger':'handle_el',
      'source': ['el_handled'],
      'dest': 'element_state',
      'conditions': 'has_next_element',
      'after': ['move_index'],},

    {'trigger':'finalize',
      'source': ['el_handled'],
      'dest': 'end_index',
      'unless': 'has_next_element',},    

    {'trigger':'end_index',
      'source': ['el_handled'],
      'dest': 'done',
      'after': ['done_processing']}
    ]




class ProcessingModel(object):
    """Processing model for an ocr page from the Resolutions
    of the States General. Methods reflect the state machine 
    transitions"""
    def __init__(self, page, p1=p1, p2=p2):
        self.page = page
        self.parsedpage = []
        self.pageposition = 0
        self.index = 0
        self.pagenr = 0
        self.current_session = Session(date='')
        self.current_resolution = Resolution('')
        self.current_footnote = []
        self.sessions = []
        self.p1 = p1
        self.p2 = p2
    
    def prepare(self):
        if not self.current_session:
            self.current_session = self.make_session(date='')
            self.current_resolution = Resolution('')
    
    def report(self):
        res  = """
        page handled: %s;
        number of sessions: %s;
        number of resolutions: %s
        """ % (self.pagenr, 
               len(self.sessions), 
               sum([len(s.resolutions) for s in self.sessions]))
        print (res)
    
    def page_state_transition(self):
        c = Counter(self.page)
        if c['X'] < 25:
            return True
        
    def move_index(self):
        if self.index <= len(self.parsedpage):
            self.index += 1
        else:
            raise IndexError
            
    def has_next_element(self):
        if self.index < len(self.parsedpage):
            return True
                   
    def divide_page_transition(self):        
        self.parsedpage = [s.strip() for s in re.split('<br\/?>\\n*', self.page) if s.strip() != '']

    def pagenumber(self):
        pat1 = re.compile('[0-9]+')
        pn = pat1.findall(self.page[:100])[0]
        if pn:
            self.pagenr = pn
        self.page = self.page[len(pn):]
        
    def make_resolution(self, text=''):
        if self.current_resolution:
            self.add_resolution_to_session()
            text = self.parsedpage[self.index]  
        else:
            text = ''
        self.current_resolution = Resolution(text)

    
    def make_session(self):
        self.sessions.append(self.current_session)
        el = self.parsedpage[self.index]
        r = p1.search(el)
        dt = ' '.join(r.groups())
        ses = Session(date=dt)
        self.current_session = ses
        
    def add_resolution_to_session(self):
        if self.current_resolution:
            a_res = self.current_resolution
            self.current_session.set_resolution(a_res)    
            self.current_resolution = None
    
    def res_cont_transition(self):
        text = self.parsedpage[self.index]
        self.current_resolution.text.append(text)
    
    def footnote_transition(self):
        self.current_resolution.footnote = True

    def handle_element(self, p):
        el = self.parsedpage[self.index]
        if p.search(el):
            return True
    
    def element_is_date(self):
#        p1 = re.compile('\A\s*(\d+)\s*(januari|februari|maart|april|mei|juni|juli|augustus|september|oktober|november|december)\s+(\d+)')
        result = self.handle_element(self.p1)
        return result
        
    def element_is_resolution(self):
        result = self.handle_element(self.p2)
        return result

    def element_is_footnote(self):
        p3 = re.compile('\d+[a-c]+')
        result = self.handle_element(p3)
        return result    
        
    def element_is_c_res(self):
        p4 = re.compile('.*')
        return self.handle_element(p4)   

    def done_processing(self):
        self.sessions.append(self.current_session)
        

def make_date(text):
    try:
        date = dateparse(text)
    except ValueError:
        date = None
    return (text, date)
    
def parse(fl,
          pat,
          states=states,
          transitions=transitions, 
          log = True):
    """parses file
    The transitions and states for the machine are defined above"""
    if log == True:
        fn = os.path.join('/Users/rikhoekstra/surfdrive/rsg/ocr/','rsg_parser.log')
        logging.basicConfig(filename=fn,filemode='w',level=logging.INFO)
        logging.getLogger('transitions').setLevel(logging.INFO)
    page = fl.read()
    fl.close()
    
    model = ProcessingModel(page, p2=pat)
    machine = Machine(model=model,
                      transitions=transitions,
                      initial='start',)
    states=states
    machine.add_states(states, ignore_invalid_triggers=True)
    try:
        model.d_page()
        model.divide()
        while model.has_next_element():
            model.check_date()
            model.check_resolution()
            model.check_footnote()
            model.check_cont_resolution()
            model.handle_el()
#        import pdb; pdb.set_trace()
        model.finalize()
        model.end_index()
    
    except IndexError:
        pass
    model.done_processing()
    return model
    
    

