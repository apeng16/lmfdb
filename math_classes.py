# -*- coding: utf-8 -*-

from base import getDBConnection, app
from utils import url_for
from databases.Dokchitser_databases import Dokchitser_ArtinRepresentation_Collection, Dokchitser_NumberFieldGaloisGroup_Collection
from sage.all import PolynomialRing, QQ

class ArtinRepresentation(object):
    @staticmethod
    def collection(source = "Dokchitser"):
        if source == "Dokchitser":
            return Dokchitser_ArtinRepresentation_Collection(getDBConnection())
    
    def __init__(self, *x, **data_dict):
        if len(x) == 0:
            # Just passing named arguments
            self._data = data_dict["data"]
        else:
            self._data = self.__class__.collection().find_and_convert_one(Dim = int(x[0]), Conductor = str(x[1]), DBIndex = int(x[2]))

    @classmethod
    def find(cls, *x, **y):
        for item in cls.collection().find_and_convert(*x, **y):
            yield ArtinRepresentation(data = item)
    
    @classmethod
    def find_one(cls, *x, **y):
        return ArtinRepresentation(data = cls.collection().find_and_convert_one(*x, **y))    
    
    def dimension(self):
        return self._data["Dim"]
    
    def conductor(self):
        return self._data["Conductor"]
    
    def index(self):
        return self._data["DBIndex"]
        
    def number_field_galois_group(self):
        if not hasattr(self,"_number_field_galois_group"):
            tmp = self._data["NFGal"]
            query = {"TransitiveDegree" : int(tmp[0]), "Size" : str(tmp[1]), "DBIndex": int(tmp[2])}
            self._number_field_galois_group = NumberFieldGaloisGroup.find_one(query)
        return self._number_field_galois_group
    
    def is_ramified(self, p):
        return self.number_field_galois_group().discriminant() % p == 0
    
    def euler_polynomial(self,p):
        """
            Returns the polynomial at the prime p in the Euler product. Output is as a list of length the degree (or more), with first coefficient the independent term.
        """
        if self.is_ramified(p):
            return [1,1]
        else:
            return [1]
        
    def coefficients_list(self, upperbound = 100):
        from sage.rings.all import RationalField
        from utils import an_list
        return an_list(lambda p: self.euler_polynomial(p), upperbound = upperbound, base_ring = RationalField())

    def character(self):
        return CharacterValues(self._data["Character"])
    
    def __str__(self):
        try:
            return "An Artin representation of conductor "+\
                    str(self.conductor())+" and dimension "+str(self.dimension())
            #+", "+str(self.index())
        except:
            return "An Artin representation"

    def title(self):
        try:
            return "An Artin representation of conductor $"+\
                    str(self.conductor())+"$ and dimension $"+str(self.dimension())+"$"
        except:
            return "An Artin representation"
    
    def url_for(self):
        from artin_representations import artin_representations_page
        from artin_representations.main import *
        return url_for("artin_representations.by_data", dim = self.dimension(), conductor = self.conductor(), index = self.index())
        
    def langlands(self):
        """
            Tim:    conjectured always true,
                    known in dimension 1,
                    most cases in dimension 2
            Andy:   
        """
        return True

    def sign(self):
        # Guessing needs to be implemented here
        return 1
        raise NotImplementedError
    
    def trace_complex_conjugation(self):
        """ Computes the trace of complex conjugation, and returns an int
        """
        tmp = (self.character()[self.number_field_galois_group().index_complex_conjugation()-1])
        try:
            assert len(tmp) == 1
            trace_complex = tmp[0]  
        except AssertionError:            
        # We are looking for the character value on the conjugacy class of complex conjugation.
        # This is always an integer, so we don't expect this to be a more general algebraic integer, and we can simply convert to sage
            raise TypeError, "Expecting a character values that converts easily to integers, but that's not the case: %s"% tmp
        return trace_complex
    
    def number_of_eigenvalues_plus_one_complex_conjugation(self):
        return int((self.dimension() + self.trace_complex_conjugation())/2)
    
    def number_of_eigenvalues_minus_one_complex_conjugation(self):
        return int((self.dimension() - self.trace_complex_conjugation())/2)
        
    def kappa_fe(self):
        return [1/2 for i in range(self.dimension())]
    
    def lambda_fe(self):
        return [0 for i in range(self.number_of_eigenvalues_plus_one_complex_conjugation())] + \
                    [1/2 for i in range(self.number_of_eigenvalues_minus_one_complex_conjugation())]
    
    def primitive(self):
        return True

    def mu_fe(self):
        return []
        raise NotImplementedError
        
    def nu_fe(self):
        return []
        raise NotImplementedError
    
    def self_dual(self):
        return True
        raise NotImplementedError
    
    def selfdual(self):
        return self.self_dual()
    
    def poles(self):
        if self.conductor() == 1 and self.dimension() ==1:
            raise NotImplementedError
            # needs to return the pole in the case of zeta
        return []
    
    def residues(self):
        if self.conductor() == 1 and self.dimension() ==1:
            raise NotImplementedError
            # needs to return the pole in the case of zeta
        return []
    
    
class CharacterValues(list):
    def display(self):
        # The character values can be large, do not convert to int!
        return "["+",".join([x.latex() for x in self])+"]"
    
class ConjugacyClass(object):
    def __init__(self,G,data):
        self._G = G
        self._data = data
    
    def group(self):
        return self._G
    
    def size(self):
        return self._data["Size"]
    
    def order(self):
        return self._data["Order"]
        
    def representative(self):
        return self._data["Representative"]
        
    def __str__(self):
        try:
            return "A conjugacy class in the group %s, of order %s and with representative %s"%(G,self.order(),self.representative())
        except:
            return "A conjugacy class"
        
    

class G_gens(list):
    def display(self):
        return self
        
class NumberFieldGaloisGroup(object):
    @staticmethod
    def collection(source = "Dokchitser"):
        if source == "Dokchitser":
            tmp = Dokchitser_NumberFieldGaloisGroup_Collection(getDBConnection())
            return tmp
            
    
    def __init__(self, *x, **data_dict):
        self._data = data_dict["data"]
            
    @classmethod
    def find_one(cls, *x, **y):
        return NumberFieldGaloisGroup(data = cls.collection().find_and_convert_one(*x, **y))    
    
    @classmethod
    def find(cls, *x, **y):
        for item in cls.collection().find_and_convert(*x, **y):
            yield NumberFieldGaloisGroup(data = item)
    
    def degree(self):
        return self._data["TransitiveDegree"]
    
    def polynomial(self):
        return self._data["Polynomial"]
                
    def polredabs(self):
        if "polredabs" in self._data.keys():
            return self._data["polredabs"]
        else:
            pol = PolynomialRing(QQ,'x')(self.polynomial())
            pol *= pol.denominator()
            R = pol.parent()
            from sage.all import pari
            pol = R(pari(pol).polredabs())
            self._data["polredabs"] = pol
            return pol
    
    def label(self):
        if "label" in self._data.keys():
            return self._data["label"]
        else:
            from number_fields.number_field import poly_to_field_label
            pol = PolynomialRing(QQ,'x')(self.polynomial())
            label =  poly_to_field_label(pol)
            if label:
                self._data["label"] = label
            return label
    
    def url_for(self):
        from number_fields import nf_page
        from number_fields.number_field import *
        if self.label():
            return url_for("number_fields.by_label", label = self.label())
        else:
            None
    
    def size(self):
        return self._data["Size"]
    
    def index(self):
        """
        The index in the database among entries with the same degree and group.
        """
        return self._data["DBIndex"]
        
    def G_gens(self):
        """
        Generators of the Galois group
        """
        return G_gens(self._data["G-Gens"])
        
    def G_name(self):
        """
        Standardized name of the abstract group
        """
        return self._data["G-Name"]
        
    def computation_data(self):
        return tuple([self._data[k] for k in ["QpRts-p", "QpRts-minpoly", "QpRts-prec", "QpRts"]])
    
    def residue_characteristic(self):
        return self._data["QpRts-p"]
    
    def computation_precision(self):
        return self._data["QpRts-prec"]
        
    def computation_minimal_polynomial(self):
        return self._data["QpRts-minpoly"]

    def computation_roots(self):
        tmp =  [str(x)  for x in self._data["QpRts"]]
        return tmp
        
    def index_complex_conjugation(self):
        # This is an index starting at 1
        return self._data["ComplexConjugation"]
        
    def Frobenius(self):
        return self._data["Frobs"]

    def Frobenius_resolvents(self):
        return self._data["FrobResolvents"]
        
    def conjugacy_classes(self):
        return [ConjugacyClass(self.G_name(),item) for item in self._data["ConjClasses"]]
    
    def artin_representations(self):
        x = [ArtinRepresentation.find_one({"Dim":item["Dim"], "Conductor":str(item["Conductor"]), "DBIndex":item["DBIndex"]})\
                for item in self._data["ArtinReps"]]
        return x
        
    def discriminant(self):
        return self.sage_object().discriminant()
        
    def sage_object(self):
        from sage import *
        X = PolynomialRing(QQ,"x")
        from sage.rings.number_field.number_field import NumberField
        return NumberField(X(self.polynomial()),"x")
    
    def from_type_to_cycle_index_fn(self):
        # Returns an index starting a 1
        resolvents = self.Frobenius_resolvents()
        # Slow below
        def tmp(cycle):
            return [d for d in resolvents if d["CycleType"] == cycle][0]["Classes"]
        return tmp
    
    def from_cc_index_to_polynomial_fn(self, polynomial):
        def tmp(conjugacy_class_index):
            pass
        return  tmp
            
        
    
    def frobenius_cycle_type(self, p):
        try:
            assert not self.discriminant() % p == 0
        except:
            raise AssertionError, "Expecting a prime not dividing the discriminant", p
        return self.residue_field_degrees(p)

    def frobenius_CC_index(self, p):
        cycle_type = self.frobenius_cycle_type(p)
        self._data[""]
    
    def increasing_frobenius_cycle_type(self, p):
        return sorted(self.frobenius_cycle_type(p), reverse = True)
        
    def residue_field_degrees(self, p):
        """ This function returns the residue field degrees at p.
        """
        if not hasattr(self, "_residue_field_degree"):
            from number_fields.number_field import residue_field_degrees_function
            self._residue_field_degrees = residue_field_degrees_function(self.sage_object())
        return self._residue_field_degrees(p)
    
    
    
    def __str__(self):
        try:
            tmp = "The Galois group of the number field  Q[x]/(%s)"%self.polynomial()
        except:
            tmp = "The Galois group of a number field"
        return tmp
    
    def display_title(self):
        return "The Galois group of the number field $\mathbb{Q}[x]/(%s)"%self.polynomial().latex()+"$"
    