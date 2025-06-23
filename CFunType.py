import abc
# Функция печати значения с заменой неинициализированного (нулевого) значения пробелами для строк
def str_nspace_str (szn,n=3,zstr='',spref='',nv='<'):   
    if szn ==zstr:
      return ' '.rjust(n+len(spref))
    else:
      return f'{spref}{szn:{nv}{n}s}'
# Функция печати значения с заменой неинициализированного (нулевого) значения пробелами для вещественных 
# k- добавка на единицы измерения
def str_nspace_f0 (zn,n=3,sei='',zf=0.,spref='',nv='>' ):   
    if zn ==zf :
      return ' '.rjust(n+len(sei)+len(spref))
    else:
      return f'{spref}{zn:{nv}{n}g}{sei}'
# Функция нормализации числа номинала элемента
def norm(zn):
    if(zn!=0.):
      if zn<0.000000001 :
        return (zn*1000000000000.,'p')
      elif zn<0.000001 :
        return (zn*1000000000.,'n')
      elif zn<0.001 :
        return (zn*1000000.,'u')
      elif zn<1 :
        return (zn*1000.,'m')
      elif zn<1000 :
        return (zn,' ')
      elif zn<1000000. :
        return (zn/1000.,'K')
      else :
        return (zn/1000000.,'M')
    else :
      return (0.,' ')  
# Функция возвращает нормализованное значение номинала элемента в виде строки
def str_norm(zn,n=3,flt0=False):
    if flt0 & (zn==0.):
      return ' '.ljust(n+1)
    lnorm=norm(zn)
    return f'{lnorm[0]:>{n}g}{lnorm[1]}'  


# Базовый абстрактный класс функционального назначения электронного компонента -----
class FunType(abc.ABC):
  # Конструктор
  def __init__(self,ft):
    self.__ft=ft
  # Обязатльный к перегрузке класс   
  @abc.abstractmethod 
  def fun_type (self): pass 
  # Доступ к функциональному типу
  @property
  def ft(self):
    return self.__ft
  # Распечатать элемент   
  def __str__(self):
    return self.fun_type()

#-----------------------------------------------------------------------------------

# Элемент без параметров "Электронный компонент"-------------------------
class EC(FunType):
  # Конструктор
  def __init__(self,ft):
    super().__init__(ft)
  #  Обязательная к перегрузке функция выдачи типа компонента
  def fun_type(self):
    return self.ft
#-----------------------------------------------------------------------

# Резистор ------------------------------------------------
class R(FunType):
  @property
  def res(self):
    return self.__res
  @property
  def tol(self):
    return self.__tol
  @property
  def tcr(self):
    return self.__tcr
  # Конструктор
  def __init__(self,ft,res,tol=5.,tcr=0.):
    super().__init__(ft.replace('_',''))
    self.__res=res
    self.__tol=tol
    self.__tcr=tcr #TCR (Temperature Coefficient of Resistance).
  #  Обязательная к перегрузке функция выдачи типа компонента
  def fun_type(self):
    return 'R'+str_nspace_str(self.ft,4)
  # Распечатать элемент   
  def __str__(self):
    return 'R: '+str_norm(self.__res,4) \
                +str_nspace_f0 (self.__tol,3,'% ',0.,' ±') \
                +str_nspace_f0 (self.__tcr,4,'ppm',0. )\
                +str_nspace_str(self.ft,4,'','          ')
#-----------------------------------------------------------------


# Конденсатор ----------------------------------------------------
class C(FunType):
  @property
  def cup(self):
    return self.__cup
  @property
  def volt(self):
    return self.__volt
  @property
  def dlc(self):
    return self.__dlc
  # Конструктор
  def __init__(self,ft,cup,volt,dlc=''):
    super().__init__(ft)
    self.__cup=cup
    self.__volt=volt
    self.__dlc=dlc
  #  Обязательная к перегрузке функция выдачи типа компонента  
  def fun_type(self):
    return 'C'+str_nspace_str(self.ft,4)
   # Распечатать элемент     
  def __str__(self):
    return 'C: '+str_norm(self.__cup,4) \
                +str_nspace_f0 (self.__volt,3,'V  ',0.,'  ') \
                +str_nspace_str(self.__dlc,5,'',' ')\
                +str_nspace_str(self.ft,4,'','          ')
#-----------------------------------------------------------------


# Индуктивность ----------------------------------------------------
class L(FunType):
  @property
  def ind(self):
    return self.__ind
  @property
  def rdc(self):
    return self.__rdc
  # Конструктор
  def __init__(self,ft,ind,rdc=0,irat=0,isat=0):
    super().__init__(ft.replace('_',''))
    self.__ind=ind
    self.__irat=irat
    self.__isat=isat
    self.__rdc=rdc
  #  Обязательная к перегрузке функция выдачи типа компонента    
  def fun_type(self):
    return 'L'+str_nspace_str(self.ft,4)
  # Распечатать элемент      
  def __str__(self):
    return 'L: '+str_norm(self.__ind,4,True) \
                +str_nspace_f0 (self.__irat,4,'A  ',0.,' ') \
                +str_nspace_f0 (self.__isat,4,'A  ') \
                +str_nspace_f0 (self.__rdc,5,'ohm') \
                +str_nspace_str(self.ft,4,'',' ')
#-----------------------------------------------------------------


# Репперный знак----------------------------------------------------
class REPF(FunType):
  # Конструктор
  def __init__(self,ft):
    super().__init__(ft)
  #  Обязательная к перегрузке функция выдачи типа компонента
  def fun_type(self):
    return self.ft
 #-----------------------------------------------------------------------




def main():

  elc=[('E',47e-12,50,'NP0'),
  ('',4.7e-9,6.3,'X5R'),
  ('X',47e-6,16,'X7R'),
  ('XY',4.7e-6,25,''),
  ('P',120e-12,50,'NP0'),
  ('CXY',330e-9,6.3,'X1/Y1'),
  ('E',220e-6,16,'X7R'),
  ('',470e-6,25,'')]
  mco=[]
  for c in elc:
    mco.append(C(c[0],c[1],c[2],c[3]))
  for co in mco:
    print(co)   
    
  elr=[('_SR',0.120,5,100),
  ('',2.4,5,100.),
  ('_U',47e3,5,0.),
  ('_A',210e6,5,0.),
  (' ',0.120,1,200),
  ('',2.43,1,10),
  ('  ',51e3,1,50),
  ('',210e6,1,25)]
  mro=[]
  for r in elr:
    mro.append(R(r[0],r[1],r[2],r[3]))
  for ro in mro:
    print(ro)   
    
  ell=[('',1.5e-6,0.020,4.8,7.3),
  ('_EMS',3.3e-6,0.027,4.0,6.2),
  ('   ',1.0e-6,0.113,1.6,1.5),
  ('_EMS',2.2e-6,0.150,1.3,0.6),
  ('_EMS',300e-6,0,15,20),
  (' ',1.2e-3,2.3,100,80),
  ('',22e-3,10,14,10),
  ('',510e-3,1.3,12.5,17.3)]
  mlo=[]
  for l in ell:
    mlo.append(L(l[0],l[1],l[2],l[3],l[4]))
  for lo in mlo:
    print(lo)   

  ell=REPF('REP')  
  print(ell)


  import qrcode
# example data
  data =  'Резистор:'+str(mro[4])
  print (data)
  # output file name
  filename = "site1.png"
  # generate qr code
  img = qrcode.make(data)
# save img to a file
  img.save(filename)


if __name__ == "__main__":
    main()

