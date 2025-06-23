from CFunType import R,C,L,EC,REPF
from CMntType import SMT,THT,HMT,PCB,REPM
from CVokIndex import *
from re import findall
import re
import json
from lzstring import LZString
import hashlib

# Шаблон регулярного выражения для номинала с точкой
reg_flt=r'[\d+(?:\.\d*)]+[pnumKM]*' 
reg_CV=r'[\d+(?:\.\d*)]+V'
reg_simpl=r'[\d+(?:\.\d*)]+'
# Расшифровка номинала
def getflt(istr,pat=reg_flt):
    strf=findall(pat, istr)
    #print(strf)
    mn=1.
    l=len(strf[0]) - 1
    match strf[0][l]:
        case 'p': mn=1.e-12
        case 'n': mn=1.e-9
        case 'u': mn=1.e-6
        case 'm': mn=1.e-3
        case 'K': mn=1.e+3
        case 'M': mn=1.e+6
        case 'V': l-=1
    if mn==1.: l+=1    
    return float(strf[0][:l])*mn


# Выдача свойства по номеру с контролем его отсутствия в словаре и заменой на значение по умолчанию
def str_prop(proplist,i,zn_def=''):
    if i!=0 :
        rstr=proplist[i-1]
        if (rstr==''):
            return zn_def
        else :
            return rstr
    else :
        # в словаре не обнаружено свойство
        return zn_def
    

# Выдача значения свойства по номеру с контролем его отсутствия в словаре
def f_prop(proplist,i,zn_def=0.,j=0,pat=reg_simpl):
    if i==0 :
        return zn_def
    else :
        return str_float(str_prop(proplist,i,zn_def='0.'),j,pat)  


# Преобразование во число значения из начала строки   
def str_float(str_in,j=0,pat=reg_simpl):
    #print(str_in)
    ostr=findall(pat,str_in)[j]
    #print(ostr)
    return float(ostr)


LNAME=25
LFUNTYPE=38
#LFOOTPRINT=16
class CElComponent:
    """Класс электронного компонента"""
    @property
    def ft(self):
        return self.__fun_type
    @property
    def mt(self):
        return self.__mnt_type
    # Получить UID элемента ===============================================================================================
    @property
    def UID(self):
        return self.__UID 
    # Перегрузка равенства ================================================================================================
    def __eq__(self, value):
        return value == self.__UID
    # Hash элемента =======================================================================================================
    def __hash__(self):
        return self.UID
    # Строка ==============================================================================================================
    def __strel(self):
        return self.__name.ljust(LNAME) +str(self.__fun_type).ljust(LFUNTYPE) +str(self.__mnt_type)
    def __str__(self):
        return self.__strel()
    # Конструктор==========================================================================================================
    def __init__(self,proplist,vok,invalue='',inname=''):
         # Определяем откуда будем брать value
        if invalue=='' :
            svalue=str_prop(proplist,vok.f0)
        else :
            svalue=invalue
        # Основные поля -------------------------------
        if inname=='' :
            self.__name=str_prop(proplist,vok.name)
        else :
            self.__name=inname   
        # Обработка функционального типа компонента--------------------------------------------------------**********
        ft=str_prop(proplist,vok.ft)
        self.__fun_type=None
        match ft:
        # Резистор ------------------------------------
            case ('R'|'R_A'|'R_SR'|'R_U'):
               # Найден регулярный резистор 
                self.__fun_type=R(ft[1:],getflt(svalue),f_prop(proplist,vok.f1),f_prop(proplist,vok.f2))
                #print(self.__fun_type)
        # Кондесатор ----------------------------------
            case ('C'|'CE'|'CP'|'CX'|'CXY'):
                # Найден регулярный конденсатор 
                self.__fun_type=C(ft[1:],getflt(svalue),getflt(svalue,reg_CV),str_prop(proplist,vok.f2))
                #print(self.__fun_type)
        # Индуктивность -------------------------------
            case ('L'|'L_EMC'):
                # Найдена регулярная катушка индуктивности 
                if(svalue=='') & (ft=='L_EMC'):
                    svalue='0.' # Обход незаполненного поля для индуктивности
                self.__fun_type=L(ft[1:],getflt(svalue),f_prop(proplist,vok.f3),f_prop(proplist,vok.f4),f_prop(proplist,vok.f5))                                                        
                #print(self.__fun_type)
        # Реперный знак -------------------------------
            case ('REP'):
                # Найден реперный знак
                self.__fun_type=REPF(ft[0:])                                                        
                #print(self.__fun_type)
       # Иной элемент -------------------------------- 
            case _:
                self.__fun_type=EC(ft[0:])
                #print(self.__fun_type)
        # ---------------------------------------------
        #
        #
        #
        #Обработка компонента по типу монтажа---------------------------------------------------------------**********
        mt=str_prop(proplist,vok.mt)
        self.__mnt_type=None
        match mt:
        # Поверхностный монтаж ------------------------------------
            case ('SMT'):
                #(self,footprint,h=0.,pack='',step=0.,Q='',x=0.,y=0.)
                self.__mnt_type=SMT(str_prop(proplist,vok.footprint),f_prop(proplist,vok.m0),str_prop(proplist,vok.m3), \
                                                                     f_prop(proplist,vok.m4),str_prop(proplist,vok.m5), \
                                                                     f_prop(proplist,vok.m1),f_prop(proplist,vok.m2))
                #print(self.__mnt_type)
            case ('THT'):
        # Выводной монтаж стандартные элементы --------------------
                self.__mnt_type=THT(str_prop(proplist,vok.footprint).split('__')[0])
                #print(self.__mnt_type)
            case ('HMT'):
        # Выводной монтаж сборки ТЛАС -----------------------------
                self.__mnt_type=HMT(str_prop(proplist,vok.footprint),str_prop(proplist,vok.m3))
                #print(self.__mnt_type)
            case ('PCB'):
        # Элементы реализованные на плате -------------------------
                self.__mnt_type=PCB(str_prop(proplist,vok.footprint))
                #print(self.__mnt_type)
            #case ('REP'):
            case ('REP-2S'):
                # Реперный знак -------------------------------
                self.__mnt_type=REPM(str_prop(proplist,vok.footprint))                                                        
                #print(self.__fun_type)
        # Неопознанный тип монтажа -------------------------------- 
            case _:
                print(' *********************************** Неопознанный тип монтажа! *********************************** ')
        #---------------------------------------------------------------------------------------------------**********
        #  Вычислить UID
        self.__UID=int((hashlib.md5((self.__strel()).encode())).hexdigest(),16)
        #print(self.__UID)


#======================================================================================================================================             


#======================================================================================================================= Тест ==
    


def main():
    # Получение списка файлов для обработки
    LAUNCHDIR = 'launch'
    LAUDIR = "./"+LAUNCHDIR+"/"
    nfile='B3n2-TPb_IBOM_r1.html'
    #nfile='B3n2-MeasUDiv_IBOM_r1new.html'
    #nfile='B3n2-DC-DC_IBOM_r1new.html'
    from CElModule import CElModule
    spec=CElModule(LAUDIR+nfile)
    print(spec.report())
 
if __name__ == "__main__":
    main()





