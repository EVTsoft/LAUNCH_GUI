import abc
from CFunType import str_nspace_f0,str_nspace_str 
     
# Базовый абстрактный класс типа монтажа электронного компонента ----------------
LFOOTPRINT=16
class MntType(abc.ABC):
  # Конструктор
  def __init__(self,futprn):
    self.__fp=futprn
  @property
  def fp(self):
      return self.__fp
  # Обязатльный к перегрузке класс  
  @abc.abstractmethod 
  def mnt_type (self): pass  
  # Вывод в сторку по умолчанию
  def __str__(self):
    return self.mnt_type() +str_nspace_str(self.__fp,LFOOTPRINT,'',':')
#--------------------------------------------------------------------------------


# Класс элемента выводного монтажа -------------------------------------------  
class THT(MntType):
  # Обязатльный к перегрузке класс
  def mnt_type(self):
     return 'THT'
#-----------------------------------------------------------------------------


# Репперный знак --------------------------------------------------------------  
class REPM(MntType):
  # Обязатльный к перегрузке класс
  def mnt_type(self):
     return 'REP'
#-----------------------------------------------------------------------------


# Класс элемента-сборки выводного монтажа --------------------------------------- 
class HMT(MntType):
  # Конструктор
  def __init__(self,footprint,dn):
    super().__init__(footprint)
    self.__dec_num=dn
  # Обязатльный к перегрузке класс
  def mnt_type(self):
     return 'HMT'
  # Строка
  def __str__(self):
    return super().__str__() +'  '+self.__dec_num
#--------------------------------------------------------------------------------


# Класс PCB реализованного компонента ------------------------------  
class PCB(MntType):
  # Обязатльный к перегрузке класс
  def mnt_type(self):
     return 'PCB'
#-------------------------------------------------------------------


# Класс SMD -------------------------------------------------------------------
class SMT(MntType):
  # Конструктор
  def __init__(self,footprint,h=0.,pack='',step=0.,Q='',x=0.,y=0.):
    super().__init__(footprint)
    self.__h=h
    self.__x=x
    self.__y=y
    self.__pack=pack
    if 'tape' in pack :self.__step=step
    else: self.__step=0.
    self.__Q=Q
    # выбор головки для установщика
    __n=min([x,y])
    if(__n!=0):
      if(__n<0.8):
        self.__nozzle='N502'
      elif(__n<1.5):
        self.__nozzle='N503'
      elif(__n<4):
        self.__nozzle='N504'
      elif(__n<7):
        self.__nozzle='N505'
      else:
        self.__nozzle='N506'
    else:
      self.__nozzle=''
  # Обязатльный к перегрузке класс
  def mnt_type(self):
     return 'SMT'
  # Доступ к свойству
  @property
  def h(self):
    return self.__h
  # Доступ к свойству
  @property
  def x(self):
    return self.__x
  # Доступ к свойству
  @property
  def y(self):
    return self.__y
  # Доступ к свойству
  @property
  def pack(self):
    return self.__pack
  # Доступ к свойству
  @property
  def step(self):
    return self.__step
  # Доступ к свойству
  @property
  def q(self):
    return self.__Q
  # Доступ к свойству с возможностью установки
  @property
  def nozzle(self):
    return self.__nozzle
  @nozzle.setter
  def nozzle(self, nozzle):
    self.__nozzle = nozzle    
  # Строка    
  def __str__(self):
    return super().__str__()  +'  ' +str_nspace_str (self.__nozzle,4)       +str_nspace_f0 (self.__h,4,'',0.,'  h=' ,'<') \
                                    +str_nspace_str (self.__pack,6,'','  ') +str_nspace_f0 (self.__step,3,'',0.,'  step=' ,'<') \
                                    +str_nspace_str (self.__Q,8,'',' ')     +str_nspace_f0 (self.__x,4,'',0.,'  x=' ,'<') \
                                                                            +str_nspace_f0 (self.__y,4,'',0.,' y=' ,'<')
  #----------------------------------------------------------------------------



def main():
    el=THT('WEO001602CLPP3N00000')
    elsmd=SMT('R0603',1.,'tape8',4.,'Q1',2.,3.)
    elsmd1=SMT('SOT-23',10.1,'tape16',4.,'Q3',0.,3.)
    elsmd2=SMT('C0805',0.12,'tape8',2.,'',0.1,0.2)
    elsmd3=SMT('CDDFN10-0506N',0.45,'tape12',0.,'Q4',4.5,3.1)
    elsmd4=SMT('KPB-3025SURKCGKC',0.65,'',1.5,'Q4',2.3,1.8)
    elsmd5=SMT('WQFN-24',0.,'tape8',2.,'Q3',3.,3.)
    eltht=THT('KLS1-202E-10-S-B-L	')
    elhmt=HMT('FDC-10','ТЛАС 436121.027-06')
    elpcb=PCB('K2x2-SMD')
    print (el)
    print (elsmd)
    print (elsmd1)
    print (elsmd2)
    print (elsmd3)
    print (elsmd4)
    print (elsmd5)
    print (eltht)
    print (elhmt)
    print (elpcb)
 
    ell=REPM('REP')  
    print(ell)
 
if __name__ == "__main__":
    main()

