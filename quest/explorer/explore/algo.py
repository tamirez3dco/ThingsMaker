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

class Rows(Base):
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
    
class Axis(Base):
    def _map_params(self, params):
        #p=params
        #mapped = [p[0],p[2],p[4],p[5],p[3],p[1]]
        #mapped = [p[0],p[2],p[4],p[6],p[7],p[5],p[3],p[1]]
        mapped=[]
        for i in range(0,self.page_size,2):
            mapped.append(params[i])
        for i in range(self.page_size-1,0,-2):
            mapped.append(params[i])            
        return mapped
    
    def get_page_params(self, parent_params, ranges, param_index, iterate_type):
        step=0.1
        params_list=[]
        for i in range(0, self.page_size/2):
            params_more = list(parent_params)
            params_more[i] = min(1.0, parent_params[i]+step) 
            params_less = list(parent_params)
            params_less[i] = max(0, parent_params[i]-step) 
            params_list.append(params_less)
            params_list.append(params_more)
        
        return self._map_params(params_list)
           
class Explore(Base):
    def _min_d(self, l, params):
        minD = 1000
        for p in l:
            distance = np.linalg.norm(np.array(p)-np.array(params))
            if distance<minD:
                minD=distance
        return minD
                
    def get_page_params(self, parent_params, ranges, param_index, iterate_type):  
        r1 = ranges[0]
        r2 = ranges[1]
        #logging.warn(r2)
        num_tries = 5
        params = self._my_random_params(parent_params, r1, r2)
        params_list = [params]
        for i in range(self.page_size):
            maxD=0
            for t in range(num_tries):
                params = self._my_random_params(parent_params, r1, r2)
                minD = self._min_d(params_list, params)
                if minD>maxD:
                    maxD = minD
                    maxD_params = params  
            params_list.append(maxD_params)
    
        return params_list 

class Iterate(Base):
    def _min_d(self, l, params):
        minD = 1000
        for p in l:
            distance = np.linalg.norm(np.array(p)-np.array(params))
            if distance<minD:
                minD=distance
        return minD
                
    def _get_random_page_params(self, parent_params, ranges):  
        r1 = ranges[0]
        r2 = ranges[1]
        #logging.warn(r2)
        num_tries = 5
        params = self._my_random_params(parent_params, r1, r2)
        params_list = [params]
        for i in range(self.page_size):
            maxD=0
            for t in range(num_tries):
                params = self._my_random_params(parent_params, r1, r2)
                minD = self._min_d(params_list, params)
                if minD>maxD:
                    maxD = minD
                    maxD_params = params  
            params_list.append(maxD_params)
    
        return params_list 
    
#    def _get_param_points(self, param):
#        a = param/0.2
#        start = a - (math.floor(a) * 0.2)
#        for i in range(5):
#            point = start + (i*0.2)
            
    def get_page_params(self,  parent_params, ranges, param_index, iterate_type):
        if (iterate_type == 'random'):
            return self._get_random_page_params(parent_params, [0, 0.15])
        
        param_index = param_index % len(parent_params)
        #logging.warn(str(param_index))
        #logging.warn("Param index: %s" % param_index)
        params_list = []
        for i in range(self.page_size):
            param = i*(0.98/(self.page_size-1))+0.01
            
            params = list(parent_params)
            params[param_index] = param
            params_list.append(params)
            
        params_list2 = list(params_list)
        params_list2[2] = params_list[5] 
        params_list2[3] = params_list[2]      
        params_list2[5] = params_list[3]  
        
        return params_list2    
    
class Learn(Base):
    def get_page_params(self, parent_params, param_index, exploration_type):
        pass