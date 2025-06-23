from CFunType import R,C,L,EC,REPF
from CMntType import SMT,THT,HMT,PCB,REPM
from CElComp  import str_prop
from CElComp  import CElComponent
from CCoordinates import CXY,tCXY
from CVokIndex import *
from re import findall
from CSpecification import CSpecification
from CDesignator import CDesignator
import re
import json
from lzstring import LZString
import pickle
import os
import pprint
from tkinter import *
from CModDraw import CModDraw

class CElModule():
    """ Класс электронного модуля"""

    def __str__(self):
        return self.__NFBOM
    
    # Формируем "стандартный" отчет-----------------   
    def report(self):
        # Выводим имя файла---------------
        outstr='\n'+str(self).ljust(38)+self.__prnMD()+'\n'
        # Выводим всегда монтируемые компоненты -----------------------------------
        outstr+=self.__spec.repstd()
        # Выводим массив исполнений ----------------------------------------------- 
        for nkey in self.__l_isp:
            outstr+=f'Исполнение {nkey}:\n'
            outstr+=(self.__var_vk[nkey]).repstd()
        return outstr
    
    # Выдать спецификацию на исполнение модуля
    def GetIsp(self,nIsp=0,n=1):
        if nIsp in self.__var_vk:
            return (self.__spec + (self.__var_vk)[nIsp])*n
        else:
            return None

    # Стандартный отчет об исполнении
    def StdRepIsp(self,nIsp=0,n=1):
        sp=self.GetIsp(nIsp,n)
        if sp == None :
            return f' В модуле: {self.__NFBOM} исполнение - {nIsp} отсутствует. \n'
        else:
            return f' Модуль: {self.__NFBOM} >> Исполнение-{nIsp}:\n'+sp.repstd()

    # Расширенный отчет об исполнении  *******************************************************************************************************
    def ExtRepIsp(self,nIsp=0):
        sp=self.GetIsp(nIsp)
        if sp == None :
            return f' В модуле: {self.__NFBOM} исполнение - {nIsp} отсутствует. \n'
        else:
            #sp.getNozzle()
            return f' Модуль: {self.__NFBOM} >> Исполнение-{nIsp}:\n'+sp.repstd()

    # применяем декоратор
    @classmethod
    def Pick(cls,mod,dir=''):
        ModName=mod
        ModDir='./'
        if dir != '': ModDir=ModDir+dir+'/'
        snam=(ModName).split('_')
        NFPICK=ModDir+snam[0]+'_'+snam[1]+'.pick'      # Имя файла
        NFBOM=ModDir+snam[0]+'_IBOM_'+snam[1]+'.html'  # Имя файл
        
        if os.path.exists(NFPICK):
            print('\n',NFPICK.ljust(36),end='')
            with open(NFPICK, "rb") as fpick:
                retc=pickle.load(fpick)
        else:
            print('\n',NFBOM.ljust(36),end='')
            retc=cls(mod,dir)
        print (retc.__prnMD(),end='')    
        return retc


    # Метаданные модуля
    def __prnMD(self):
        return f' {self.__metadata['company']}   {self.__metadata['title']}.{self.__metadata['revision']}'.ljust(35) +f'  {self.__metadata['date']}    '

    # Размеры ПП
    def plt_size(self):
        return f' > SizeBoard={self.__SizeBrd}' +f' > EdgeBoard={self.__EdgeBrd}'
        #self.__EdgeBrd           # Координаты нуля платы
        #self.__SizeBrd           # Размер платы

    def addelspc(self,spc,el,n,md):
        self.__PerEl[el.UID]=md
        spc.addel(el,n)

    def __init__(self,mod,dir=''):
        self.__ModName=mod
        self.__ModDir='./'
        if dir != '': self.__ModDir=self.__ModDir+dir+'/'
        snam=(self.__ModName).split('_')
        self.__NFBOM=self.__ModDir+snam[0]+'_IBOM_'+snam[1]+'.html'      # Имя файла
        self.__NFPICK=self.__ModDir+snam[0]+'_'+snam[1]+'.pick'      # Имя файла
        self.__spec=CSpecification()    # Спецификация исполнения "all" 
        self.__var_vk={}                # Словарь целое-номер исполнения : множество-спецификация элементов
        self.__l_isp={}                 # Присутствующие в модуле номера исполнений
        self.__metadata={}              # Данные о файле из файла
        self.__PerEl={}                 # Словарь -перечень элементов модуля
        
        with open(self.__NFBOM,"r", encoding="utf-8") as file_BOM:
            lvf={} # Будущий словарь с номерами полей
            fvok=None # Индексирующий объект для адресации полей в конкретном файле
            varI=set() # Множество с исполнениями 
            for line in file_BOM:
                if(fvok==None):
                    #  поиск названий полей и определение их очередности ****************************************            
                    if '\"extra_fields\":[' in line:                # ищем начало вхождения полей AltDesigner
                        efil=line.split('\"extra_fields\":[')[1]    # отрезаем кусок строки до перечисления полей
                        efil=efil.split('],')[0]                    # отрезаем замыкающие кавычки
                        efil=re.sub(r'[\[\]"]+','',efil)            # отрезаем лишние открывающие закрывающие скобки
                        efil=efil.split(',')                        # превращаем в массив строк
                        for i, pole in enumerate(efil):
                            lvf[pole]=i                             # добавление пар название поля - его номер в словарь для модуля 
                        fvok=CVokIndex(lvf)  
                        varI=set(filter(lambda ev: findall(r'var\d+', ev[0]),lvf.items())) # ищем столбцы с вариантами
                        for vr in varI: self.__var_vk[int(vr[0][3])]=CSpecification() # добавляем в словарь множество исполнений
                else:                          
                    #  считывание элементов из файла ************************************************************
                    if "var pcbdata = JSON.parse(LZString.decompressFromBase64('" in line: # Ищем начало данных из Altium
                        bom_compress = line.replace("var pcbdata = JSON.parse(LZString.decompressFromBase64('", "")  # Удаляем префикс начала
                        bom_compress = bom_compress.replace("'));", "") # Удаляем замыкающие кавычки и разделители
                        bom = json.loads(LZString.decompressFromBase64(bom_compress)) # Разархивируем полученную информацию и грузи ее в JSON объект
                        self.__metadata=bom['metadata'].copy()

                    # Цикл синтеза компонентов модуля ***********************************************************
                        #
                        # Определяем смещение координат платы модуля и ее размер
                        self.__EdgeBrd=CXY(bom['edges_bbox']['minx'],-bom['edges_bbox']['miny'])            # Координаты нуля платы
                        self.__SizeBrd=CXY(bom['edges_bbox']['maxx'],-bom['edges_bbox']['maxy']).norm(self.__EdgeBrd)  # Размер платы   
                        #
                        # Собираем очередную позицию в спецификации
                        for elbom in bom['bom']['both']:
                            # Запоминаем массив дезигнаторов по позиции
                            mdes=[]
                            for i in range(elbom[0]):
                                ind=elbom[3][i][1]
                                if elbom[3][i][0] != bom['footprints'][ind]['ref']:
                                    print(f' >>>>>>>>>  Ошибка в дезигнаторе!!! - {elbom[3][i][0]} != {bom['footprints'][ind]['ref']}')
                                else : 
                                    xy1p=CXY()
                                    mpd=bom['footprints'][ind]['pads']
                                    pminxy=CXY(mpd[0]['pos'][0],-mpd[0]['pos'][1]).norm(self.__EdgeBrd)
                                    pmaxxy=pminxy.copy()
                                    for pd in mpd:
                                        pdxy=CXY(pd['pos'][0],-pd['pos'][1]).norm(self.__EdgeBrd)
                                        pminxy.min(pdxy)
                                        pmaxxy.max(pdxy)
                                        if 'pin1' in pd:
                                            if pd['pin1']==1 : xy1p=pdxy.copy()
                                            else : print(' >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Ошибка определения 1-го pin-а !!!')      
                                    mdes.append(CDesignator(elbom[3][i][0],bom['footprints'][ind]['layer'],bom['footprints'][ind]['bbox']['angle'],(pminxy+pmaxxy)/2,xy1p))
                            #for d in mdes :
                             #   print(d)
                            sisp=str_prop(elbom[4],fvok.vt) 
                            match sisp:
                                case 'all':     # Устанавливается всегда
                                    self.addelspc(self.__spec,CElComponent(elbom[4],fvok),elbom[0],mdes)
                                case 'DNP':     # Никогда не устанавливается
                                    pass
                                case 'var_NV':  # В присутствующих исполнениях содержатся новые имя и номинал
                                    for st in varI:
                                        sznv=elbom[4][st[1]]
                                        if sznv !='':
                                            l_NV=(re.sub(r'[()"\' ]+','',sznv)).split(',')
                                            self.addelspc(self.__var_vk[int(st[0][3])],CElComponent(elbom[4],fvok,l_NV[1],l_NV[0]),elbom[0],mdes)
                                case 'var_N':   # В присутствующих исполнениях содержится новое имя
                                    for st in varI:
                                        szn=elbom[4][st[1]]
                                        if szn !='': self.addelspc(self.__var_vk[int(st[0][3])],CElComponent(elbom[4],fvok,'',szn),elbom[0],mdes)
                                case 'var_V':   # В присутствующих исполнениях содержится новый номинал
                                    for st in varI:
                                        szv=elbom[4][st[1]]
                                        if szv !='': self.addelspc(self.__var_vk[int(st[0][3])],CElComponent(elbom[4],fvok,szv),elbom[0],mdes)
                                case _:     # В анализирем поле список исполнений в которых присутствует компонент
                                    misp=sisp.split(',')
                                    for psel in misp:
                                        isp=int(psel)
                                        if isp not in  self.__var_vk: self.__var_vk[isp]=CSpecification()
                                        self.addelspc(self.__var_vk[isp],CElComponent(elbom[4],fvok),elbom[0],mdes)
                        break
                    # -------------------------------------------------------------------------------------------
        if len(self.__var_vk)==0 : self.__var_vk[0]=CSpecification()
        self.__l_isp=[k for k in self.__var_vk.keys()]
        self.__l_isp.sort()      # Сортированное множество целых - присутствующие в модуле номера исполнений
        with open(self.__NFPICK, "wb") as fpick:
            pickle.dump(self,fpick)
            

        

    # Отчет о дезигнаторах в модуле
    def RepDz(self):
        l_mUIDs=[mUIDs for mUIDs in self.__PerEl.keys()]
        for md in l_mUIDs:
            ell= [ el for el in self.__spec.mnspec if el==md]
            print(len(ell),'    ',ell[0])
            for d in  self.__PerEl[md]:
                print(d)
        return

    
    # Отчет по монтажу SMD компонент
    def RepSMDprm(self,nIsp,side,angle=0):
        SCALE=20
        sp=self.GetIsp(nIsp)
        #----------------------
        for el in sp:
            print(el)
        #----------------------
        retSMT=sp.rep_SMD_nozzle()
        print(retSMT[0])   
        #----------------------
        c=tCXY(SCALE,self.__SizeBrd,side,angle)
        # Объект графического отображения       
        CMDraw=CModDraw(self.__ModName,c)
        #----------------------
        # Вывод элементов по дезигнаторам
        for key in retSMT[1].keys():
            print(f'>>{key}')
            for el in retSMT[1][key]:
                print('   ',el)
                for dz in self.__PerEl[el.UID]:
                    if dz.Layer==side :
                        print('                       ',dz)
                        CMDraw.DzDraw(dz,CXY(el.mt.x,el.mt.y)/2.)
        #--------------
        # Поиск, вывод и сортировка реперных знаков
        spREP=sp.rep_Rep()
        #print (len(spREP))
        for rep in spREP:
            print(rep)#,'   ',rep.mt.fp[:5])
            lst_rep=[dz for dz in self.__PerEl[rep.UID] if (dz.Layer==side) | (rep.mt.fp[:5]=='REP-D')]
            for dz_rep in  lst_rep:
                print(dz_rep)
                CMDraw.RepDraw(dz_rep,1.)
            lst_rep.sort(key=lambda d : d.XY.lvector(side,CXY(0.,0.),self.__SizeBrd))
            print('')
            for dd in lst_rep:
                print (dd)
            CMDraw.RepFL(CXY(1.1,1.1),lst_rep[0],lst_rep[-1])  
            print(self.__SizeBrd)   
        #--------------
        CMDraw.RootLoop()
        #
        return


        


#======================================================================================================================= Тест ==
    

def main():
    # Получение списка файлов для обработки 
    LAUNCHDIR = 'launch'
    #LAUDIR = "./"+LAUNCHDIR+"/"
    #nfile ='B3n2-MMI_IBOM_r1.html'
    #nfile='B3n2-Cross_IBOM_r1.html'
    #nfile='B3n2-TU_IBOM_r1.html'
    #nfile='C:/Users/tyurine.TEAMR2/Desktop/Python/GItHubUtilMain/launch/B3n2-TPb_IBOM_r1.html'
    #nfile='B3n2-MeasUDiv_IBOM_r1.html'

    #nmodule='B3n2-DC-DC_r1'#.html'
    #nmodule='B3n2-ManBot_r1'#.html'
    nmodule='B3n2-MeasUDiv_r1'#.html'

    #nfile='TestIBOM_TSU33702.html'
    #nfile='TestIBOM_TSU33701.html'
    #nfile='B3n2-IntMain_IBOM_r1.html'
    #nfile ='C:/Users/tyurine.TEAMR2/Desktop/Python/GItHubUtilMain/launch2/TestIBOM_TSU33701.html'
    #nfile ='C:/Users/tyurine.TEAMR2/Desktop/Python/GItHubUtilMain/launch2/TestIBOM_TSU33702.html'
    #nfile='C:/Users/tyurine.TEAMR2/Desktop/Python/GItHubUtilMain/launch/AC-DC-LS10_IBOM_r1.html'
    #spec=CElModule.Pick(nmodule,LAUNCHDIR)
    spec=CElModule(nmodule,LAUNCHDIR)
    #spec.RepDz()
    spec.RepSMDprm(0,'F')
    spec.RepSMDprm(0,'F',90)
    spec.RepSMDprm(0,'B')
    #print(spec.report())
    #print(spec.StdRepIsp(3))
    #print(spec.StdRepIsp(1))
    #print(spec.StdRepIsp(3,10))
    #print(spec.StdRepIsp(0))
    #print(spec.StdRepIsp(2))
    #print(spec.StdRepIsp(0,10))
    
if __name__ == "__main__":
    main()





