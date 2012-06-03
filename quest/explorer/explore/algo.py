import random
from explorer.models import GhDefinition
from django.utils import simplejson
import logging
import math
import itertools
import numpy as np

class Base:
    """
    Explore parameter space
    """
    def __init__(self, page_size=8, row_size=2):
        self.page_size = page_size
        self.row_size = row_size
       
    def get_random_page_params(self, n_params):
        params_list = []
        for i in range(self.page_size):  
            params = []      
            for j in range(n_params):
                p = float("%.2f" % random.uniform(0,1))
                params.append(p)
            params_list.append(params)
        return params_list
        
    def get_page_params(self, parent_params):
        return self.get_random_page_params(len(parent_params))
    
    def _my_random_params(self, params, r1, r2):
        rparams = []
        for v in params:
            a0 = v+r1
            b0 = min(1,v+r2)
            l0 = b0-a0
            
            a1 = max(0,v-r2)
            b1 = v-r1
            l1 = b1-a1
            ##logging.warning("l0 %s l1 %s" % (l0, l1))
            n = random.uniform(-l1,l0)
            
            sign = n/abs(n)  
            
            nn = float("%.2f" % (v+(sign*r1)+n))
            #logging.warning("n %s nn %s" % (n, nn))    
            rparams.append(nn)
            
        return rparams   

    def _mrange_random_params(self, params, r1, r2):
        rparams = []
        #for v in params:
        for i in range(len(params)):
            v = params[i]
            a0 = v+r1[i]
            b0 = min(1,v+r2[i])
            l0 = b0-a0
            
            a1 = max(0,v-r2[i])
            b1 = v-r1[i]
            l1 = b1-a1
            ##logging.warning("l0 %s l1 %s" % (l0, l1))
            n = random.uniform(-l1,l0)
            
            sign = n/abs(n)  
            
            nn = float("%.2f" % (v+(sign*r1[i])+n))
            #logging.warning("n %s nn %s" % (n, nn))    
            rparams.append(nn)
            
        return rparams   
    
class Test(Base):
    def get_page_params(self, parent_params):    
        n_rows = int(math.ceil(float(self.page_size) / float(self.row_size)))
        num_tries = 5
        params_list = []
        for j in range(n_rows):
            r1=j*0.1
            r2=(j+1)*0.1
            params = self._my_random_params(parent_params, r1, r2)
            row_params = [params]
            params_list.append(params)
            for i in range(self.row_size-1):
                maxD = 0
                for t in range(num_tries):
                    params = self._my_random_params(parent_params, r1, r2)
                    minD = 1000
                    for o in range(len(row_params)):
                        distance = np.linalg.norm(np.array(row_params[o])-np.array(params))
                        if distance<minD:
                            minD=distance
                    if minD>maxD:
                        maxD = minD
                        maxD_params = params
                row_params.append(maxD_params)
                params_list.append(maxD_params)
        
        
        return params_list  
     
class Directions(Base):
    def _min_d(self, l, params):
        minD = 1000
        for p in l:
            distance = np.linalg.norm(np.array(p)-np.array(params))
            if distance<minD:
                minD=distance
        return minD
                
    def get_page_params(self, parent_params, gp_params, ranges): 
        if gp_params != None:
            logging.warn(simplejson.dumps(gp_params)) 
            gp_diff = np.abs(np.array(gp_params)-np.array(parent_params))
            logging.warn("gp_diff: %s" % simplejson.dumps(list(gp_diff)))
            gp_diff[gp_diff>0.3] = 0.3
            gp_diff[gp_diff<0.07] = 0.07
            r1 = [0 for i in range(len(parent_params))]
            r2 = list(gp_diff)
        else:
            r1 = [ranges[0] for i in range(len(parent_params))]
            r2 = [ranges[1] for i in range(len(parent_params))]
        
        logging.warn("r1: %s" % simplejson.dumps(r1))
        logging.warn("r2: %s" % simplejson.dumps(r2))
        
        num_tries = 5
        params = self._mrange_random_params(parent_params, r1, r2)
        params_list = [params]
        for i in range(self.page_size):
            maxD=0
            for t in range(num_tries):
                params = self._mrange_random_params(parent_params, r1, r2)
                minD = self._min_d(params_list, params)
                if minD>maxD:
                    maxD = minD
                    maxD_params = params  
            params_list.append(maxD_params)
    
        return params_list
        return list(itertools.chain(*[params_list,op_list]))
            
                
            
            