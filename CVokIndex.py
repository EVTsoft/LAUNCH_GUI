
def i_pole(key,voc):
    """Функция вывода из списка поля по ключевому слову из словаря"""
    if key in voc:
        return 1+voc[key]
    else:
        return 0


class CVokIndex():
    def __init__(self,vok):
        self.__name=i_pole('Comment',vok)
        self.__footprint=i_pole('Footprint',vok)
        # FunType-----------------------------
        self.__ft=i_pole('f_type',vok)
        self.__f0=i_pole('fp0_value',vok)
        self.__f1=i_pole('fp1_tol',vok)
        self.__f2=i_pole('fp2_tc',vok)
        self.__f3=i_pole('fp3',vok)
        self.__f4=i_pole('fp4',vok)
        self.__f5=i_pole('fp5',vok)
        # MntType------------------------------
        self.__mt=i_pole('m_type',vok)
        self.__m0=i_pole('mp0_H',vok)
        self.__m1=i_pole('mp1_X',vok)
        self.__m2=i_pole('mp2_Y',vok)
        self.__m3=i_pole('mp3_pack',vok)
        self.__m4=i_pole('mp4_st',vok)
        self.__m5=i_pole('mp5_Q',vok)
        # VarTy--------------------------------
        self.__vt=i_pole('var_type',vok)
        self.__v0=i_pole('var0',vok)
        self.__v1=i_pole('var1',vok)
        self.__v2=i_pole('var2',vok)
        self.__v3=i_pole('var3',vok)
        self.__v4=i_pole('var4',vok)
        self.__v5=i_pole('var5',vok)
        
    # Функциональные свойства ------------------
    @property
    def name(self):
        return self.__name
    @property
    def footprint(self):
        return self.__footprint
    # Функциональные свойства -------------------
    @property
    def ft(self):
        return self.__ft
    @property
    def f0(self):
        return self.__f0
    @property
    def f1(self):
        return self.__f1
    @property
    def f2(self):
        return self.__f2
    @property
    def f3(self):
        return self.__f3
    @property
    def f4(self):
        return self.__f4
    @property
    def f5(self):
        return self.__f5
    # Монтажные свойства --------------------------  
    @property
    def mt(self):
        return self.__mt
    @property
    def m0(self):
        return self.__m0
    @property
    def m1(self):
        return self.__m1
    @property
    def m2(self):
        return self.__m2
    @property
    def m3(self):
        return self.__m3
    @property
    def m4(self):
        return self.__m4
    @property
    def m5(self):
        return self.__m5
    # Вырианты исполнения -------------------------
    @property
    def vt(self):
        return self.__vt
    @property
    def v0(self):
        return self.__v0
    @property
    def v1(self):
        return self.__v1
    @property
    def v2(self):
        return self.__v2
    @property
    def v3(self):
        return self.__v3
    @property
    def v4(self):
        return self.__v4
    @property
    def v5(self):
        return self.__v5
    
