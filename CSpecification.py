from CFunType import R,C,L,EC,REPF
from CMntType import SMT,THT,HMT,PCB,REPM


# Рассортировать элементы из библиотеки сначала по первому параметру потом по второму
def sortP1P2(liba,get_fpar,get_spar,cond = lambda p: True):
    lP1=list(set([get_fpar(el) for el in liba]))
    lP1.sort()
    retdata=[]
    for t in lP1:
        tmp=[el for el in liba  if (get_fpar(el)==t) & cond(el)]
        tmp.sort(key=get_spar)
        retdata+=tmp
    return retdata 

# Выбрать из списка элементы заданных классов по типу монтажа и функциональному типу, рассортировать их по двум параметрам
def mk_el_list(spec,mtype,ftype,gfP1,gfP2,cond = lambda p: True):
    sp_ret=sortP1P2([el for el in spec if isinstance(el.mt,mtype) & isinstance(el.ft,ftype)],gfP1,gfP2,cond)
    return sp_ret

def mk_el_listREP(spec):
    return mk_el_list(spec,REPM,REPF,lambda p: 0,lambda p: 0)

def mk_el_listEC(spec,I,fP2=lambda p: 0,cond = lambda p: True):
    return mk_el_list(spec,I,EC,lambda p: (p.ft).fun_type(),fP2,cond)

def mk_el_listRLC(spec,I,cond = lambda p: True):   
    return    mk_el_list(spec,I,R, lambda p: (p.ft).tol,        lambda p: (p.ft).res,cond) \
            + mk_el_list(spec,I,C, lambda p: (p.ft).volt,       lambda p: (p.ft).cup,cond) \
            + mk_el_list(spec,I,L, lambda p: (p.ft).fun_type(), lambda p: (p.ft).ind,cond)

def mk_el_listRLCEC(spec,I,fP2=lambda p: 0,cond = lambda p: True):   
    return    mk_el_listRLC(spec,I,cond)    \
            + mk_el_listEC(spec,I,fP2,cond)

 # Создание списка по заданным параметрам
def make_SMT_lst(sp,fPAR,fEQ,qsort=False,fl_rcl='ALL'):
    lst_sp=[]
    match  fl_rcl :
        case 'ALL': lst_sp=mk_el_listRLCEC(sp,SMT,fPAR, fEQ)
        case 'RCL': lst_sp=mk_el_listRLC(sp,SMT,fEQ)
        case 'EC' : lst_sp=mk_el_listEC(sp,SMT,fPAR, fEQ)
        case _    : return '\n---Нет заказанной формы отчета!---\n'
    if qsort==True :
        lst_sp.sort(key=lambda el: sp.PrElvk[el.UID])
        lst_sp.reverse()
    return lst_sp

LHASH=5
class CSpecification():

    def __init__(self,ispec=set(),iPrElvk={}):
        self.__mnspec=ispec.copy()
        self.__PrElvk=iPrElvk.copy()
        
    
    #def __str__(self):  
     #   outstr=''   
      #  for i,el in enumerate(self.__mnspec):
       #     outstr+=(f'{(i+1):>3g}. '+ f' {self.__PrElvk[el.UID]:>6g}  '+str(el).ljust(LHASH)+'\n')
        #return outstr    
    
    def __iter__(self):
        return iter(self.__mnspec)

    @property
    def mnspec(self):
        return self.__mnspec

    @property
    def PrElvk(self):
        return self.__PrElvk
  
    # Вывод элементов текущей спецификации согласно упорядоченного списка
    def str_sp(self,lst):
        outstr=''   
        for i,el in enumerate(lst):
            outstr+=(f'{(i+1):>3g}. '+ f' {self.__PrElvk[el.UID]:>6g}  '+str(el).ljust(LHASH)+'\n')
        return outstr

    # Стандартный отчет по элементам в строку
    def repstd(self):
        sp_ret= mk_el_listRLCEC(self,SMT,lambda p: (p.mt).pack) \
                         + mk_el_listRLCEC(self,THT) \
                         + mk_el_listEC(self,HMT)
        return self.str_sp(sp_ret)    
      
    
    # Oтчет по элементам SMD в заданной упаковке
    def rep_SMD_pack(self,mpack=('tape8','tape12','tape16','tape24','tray','tube','misc.','tape32','tape88'),qsort=False,fl_rcl='ALL'):
        sret=''
        for pack in mpack:
            PAR=lambda p: (p.mt.pack).strip()
            EQ= lambda p: pack==PAR(p)
            lst_sp=make_SMT_lst(self,PAR,EQ,qsort,fl_rcl)
            if len (lst_sp)!=0 :   
                sret+='>'+pack+':\n'    
                sret+=self.str_sp(lst_sp)
        return sret
    
    # Отчет по SMD компонентам по головкам
    def rep_SMD_nozzle(self,mNozzle=('N502','N503','N504','N505','N506'),qsort=True,fl_rcl='ALL'):
        sret=''
        NozzleVk={}
        for nozzle in mNozzle:
            PAR=lambda p: p.mt.nozzle
            EQ= lambda p: nozzle==PAR(p)
            lst_sp=make_SMT_lst(self,PAR,EQ,qsort,fl_rcl)
            if len (lst_sp)!=0 :  
                NozzleVk[nozzle]=lst_sp 
                sret+='>'+nozzle+':\n'    
                sret+=self.str_sp(lst_sp)
        return (sret,NozzleVk)


    # Вернуть все реперные знаки
    def rep_Rep(self):
        return mk_el_listREP(self)   

    # Расчет общих позиций в 2-х спецификациях
    def correlation(self,ispec):
        spec=(self.__mnspec).intersection(ispec.mnspec)
        PrElvk={}
        for el in spec:
            PrElvk[el.UID]=self.__PrElvk[el.UID]+ispec.__PrElvk[el.UID]
        return CSpecification(spec,PrElvk)

#--------------------------------------------------------------------------------------------
# Добавление нового элемента в множество или изменение колличества уже существующего элемента
    def addel(self,elf,n):
        if elf not in self.__mnspec :
            # Новый элемент спецификации
            self.__mnspec.add(elf)
            self.__PrElvk[elf.UID]=n
            return False
        else : 
            # Просто увеличиваем число элементов в словаре
            self.__PrElvk[elf.UID]+=n
            return True    

    def get_nelem(self):
        return len(self.__mnspec)

#---------------------------------------------------------------------------------------- Операции:
    # Добавление в текущую спецификацию дополнительной спецификации
    def addspec(self,ispec):
        olds=(self.__mnspec).intersection(ispec.mnspec)
        for el in olds: self.__PrElvk[el.UID]+=ispec.__PrElvk[el.UID]
        news=(ispec.mnspec).difference(self.__mnspec)
        self.__mnspec=(self.__mnspec).union(news)
        for el in news:self.__PrElvk[el.UID]=ispec.__PrElvk[el.UID]
    # Вычитание из текущей спецификацию дополнительной спецификации
    def subspec(self,ispec):
        olds=(self.__mnspec).intersection(ispec.mnspec)
        for el in olds:
            if(self.__PrElvk[el.UID]<=ispec.__PrElvk[el.UID]): 
                del self.__PrElvk[el.UID]
                self.__mnspec.remove(el)
            else:
                self.__PrElvk[el.UID]-=ispec.__PrElvk[el.UID]
                
    # Добавить к спецификации спецификацию, вернуть новую
    def __add__(self,a_spec):       
        spec_ret=CSpecification(a_spec.mnspec,a_spec.PrElvk)
        spec_ret.addspec(self)
        return spec_ret
    # Добавить к своей спецификации спецификацию
    def __iadd__(self,a_spec):       
        self.addspec(a_spec)
        return self
    
    # Вычесть из спецификации спецификацию, вернуть новую
    def __sub__(self,a_spec):       
        spec_ret=CSpecification(self.mnspec,self.PrElvk)
        spec_ret.subspec(a_spec)
        return spec_ret
    # Вычесть из своей спецификации спецификацию
    def __isub__(self,a_spec):       
        self.subspec(a_spec)
        return self

    # Задать колличество модулей в спецификации
    def __mul__(self,n=1):
        spec_ret=CSpecification(self.__mnspec,self.__PrElvk)
        for el in spec_ret.__mnspec: spec_ret.PrElvk[el.UID]*=n
        return spec_ret
    # Задать колличество модулей в своей спецификации
    def __imul__(self,n=1):
        for el in self.__mnspec: self.PrElvk[el.UID]*=n
        return self



def main():
    pass
    
if __name__ == "__main__":
    main()
