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
from itertools import zip_longest

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
        #if os.path.exists(self.__NFPICK):
            #os.remove(self.__NFPICK)
            #print(f"Удален pick файл -{self.__NFPICK}")
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
    def RepSMDprm(self,nIsp,side,angle=0,scl=10,max_nz=60,tst=False):
        SCALE=scl
        sp=self.GetIsp(nIsp)
        #----------------------
        retSMT=sp.rep_SMD_nozzle()
        #----------------------
        print(f'Размер печатной платы: {self.__SizeBrd} mm.')
        c=tCXY(SCALE,self.__SizeBrd,side,angle)
        # Объект графического отображения       
        CMDraw=CModDraw(self.__ModName,c)
        #----------------------
         # Поиск, вывод и сортировка реперных знаков
        all_list_rep=[]
        spREP=sp.rep_Rep()
        for rep in spREP:
            lst_rep=[dz for dz in self.__PerEl[rep.UID] if (dz.Layer==side) | (rep.mt.fp[:5]=='REP-D')]
            all_list_rep+=lst_rep
            for dz_rep in  lst_rep:
                 CMDraw.RepDraw(dz_rep,1.)
        all_list_rep.sort(key=lambda d : c.lvector(d.XY))
        m1=all_list_rep[0]
        CMDraw.set0plt(m1.XY)
        m2=all_list_rep[-1]
        CMDraw.RepFL(CXY(1.1,1.1),m1,m2)  
        First_str=f'Designator,Footprint,Center-X(mm),Center-Y(mm),Layer,Rotation,Comment'
        nxy=c.tr_plt_nscale(m1.XY)
        Rep1_xy=c.tr_plt_nscale(m1.XY).norm_round(nxy)
        Rep2_xy=c.tr_plt_nscale(m2.XY).norm_round(nxy)
        Rep1_str=f'm1,MARK_PIX,{Rep1_xy.x},{Rep1_xy.y},T,{c.tr_angle(m1.Angle):g},{m1.Des}'
        Rep2_str=f'm2,MARK_PIX,{Rep2_xy.x},{Rep2_xy.y},T,{c.tr_angle(m2.Angle):g},{m2.Des}'
        #---------------------- 
        print('\n') 
        Noz_El_vk={}
        # Вывод элементов по дезигнаторам
        for nozzle in retSMT[1].keys():
            # Перебераем головки установщика 
            Noz_El_vk[nozzle]=[]
            for el in retSMT[1][nozzle]:
                # Для каждой головки итерируем список компоненнтов
                #print('   ',el)
                el_str=el.mt.fp.strip().replace(' ','_')
                el_ft=el.prm_type()
                #print(el_ft)
                for dz in self.__PerEl[el.UID]:
                    # Для каждого компонента итерируем список дезигнаторов
                    if dz.Layer==side : # Отсекаем те, которые находятся не на выводимой стороне.
                        #print('                       ',dz)
                        delXY=c.tr_plt_nscale(dz.XY).norm_round(nxy)
                        Noz_El_vk[nozzle].append(str(f'{dz.Des},{el_str},{delXY.x},{delXY.y},T,{c.tr_angle(dz.Angle):g},{el_ft}'))
                        CMDraw.DzDraw(dz,CXY(el.mt.x,el.mt.y)/2.,nozzle)   
                    if tst: # Если это генерация тестовой программы, то выходим после одного дезигнатора на компонент
                        break    
            kel=len(Noz_El_vk[nozzle])
            if kel==0: del Noz_El_vk[nozzle]              
            print(f'На головке-{nozzle} всего элементов: {kel}')                    
        #--------------
        # Подготовка массива пар головок
        MNoz=[]
        lst_nz=[]
        for nzll in Noz_El_vk.keys():
            lst_nz.append((nzll,len(Noz_El_vk[nzll])))
        lst_nz.sort(key=lambda i : i[1],reverse=True)
        #pprint.pprint(lst_nz)
        # отсортированный по элементам список головок
        nchet=len(lst_nz)%2
        iterator=iter(lst_nz)
        for nzp in iterator:
            if (nzp[1]>=max_nz) | (nchet==1):
                # Превышен порог в головке или у нас нечетное число головок
                nchet=(nchet+1)%2
                MNoz.append((nzp[0],nzp[0]))
            else:
                MNoz.append((nzp[0],next(iterator)[0]))   
        #pprint.pprint(MNoz)
        print(f'Будут сгенерированны программы для следующих пар головок - {MNoz}')             
        #--------------
        if(len(MNoz)!=0):
            # Генерация программы для установщика SMD
            DirName=f'{self.__metadata['title']}.{self.__metadata['revision']}'.replace('.','(') +f')_{self.__metadata['date']}'.replace(' ','-').replace(':','!').replace('.','!')
            print(f'Каталог модуля: \"{DirName}\"')
            for N_Prm in MNoz:
                # Проверка наличия очередной пары головок в программе установщика
                if all(k in Noz_El_vk for k in N_Prm):
                    NamePrm=side+f'-{angle}'+'-'+N_Prm[0]+'_'+N_Prm[1]
                    if tst:
                        NamePrm='tst_'+NamePrm
                    print(f'\nГенерация программы установщика PnP {NamePrm}')
                    N0_lst=[]
                    N1_lst=[]
                    # Для каждой пары головок
                    if(N_Prm[0]!=N_Prm[1]):
                        # Отработка разных головок
                        N0_lst=Noz_El_vk[N_Prm[0]].copy()
                        N1_lst=Noz_El_vk[N_Prm[1]].copy()
                        print(f'Всего элементов: {len(N0_lst)+len(N1_lst)}. На головке-{N_Prm[0]} ({len(N0_lst)}) и головке-{N_Prm[1]} ({len(N1_lst)})')
                    else:
                        # Отработка одинаковых головок
                        nz_keys=N_Prm[0]
                        prev_el0=''
                        i_el0=0
                        prev_el1=''
                        i_el1=0
                        for elstr in Noz_El_vk[nz_keys]:
                            def addel(lst, i):
                                lst.append(elstr.strip())
                                return i+1
                            els=elstr.split(',')
                            el=els[1]+'_'+els[6]
                            #print(el)
                            if   el==prev_el0 : i_el0=addel(N0_lst,i_el0)
                            elif el==prev_el1 : i_el1=addel(N1_lst,i_el1)
                            else:
                                if i_el0<=i_el1 :
                                    prev_el0=el
                                    i_el0=addel(N0_lst,i_el0)  
                                else:
                                    prev_el1=el
                                    i_el1=addel(N1_lst,i_el1)
                        print(f'Всего элементов: {i_el0+i_el1} на головке-{nz_keys}')
                    # Генерация непосредственно программы для станка  
                    str_prm=[str(First_str),str(Rep1_str),str(Rep2_str)]
                    for crt in zip_longest(N0_lst, N1_lst): 
                        def out(ct):
                            if ct!=None:
                                str_prm.append(ct)
                        out(crt[0])
                        out(crt[1])    
                    #----------------------------------
                    # Запись созданной программы на диск
                    nside='/TOP'
                    if side=='B': nside='/BOTTOM'
                    NameDir=self.__ModDir+'PnP/'+ DirName+nside
                    FullName=NameDir+'/'+NamePrm+'.csv'
                    print(FullName)
                    if not os.path.exists(NameDir):
                        os.makedirs(NameDir)
                    with open(FullName, "w",encoding='utf-8') as fprm: 
                        for sp in str_prm:
                            fprm.write(sp)
                            fprm.write('\n')
                    #----------------------------------
                    # Вывести в  txt файл расклад компонент по головкам
                    if not tst:
                        rasklad_nz=[]
                        rasklad_nz.append(f'\nНа головке №1 - {N_Prm[0]} Следующие компоненты:')
                        els_0=list(set([el.split(',')[1]+' '+el.split(',')[6] for el in N0_lst]))
                        els_0.sort()
                        rasklad_nz+=els_0
                        rasklad_nz.append(f'\nНа головке №2 - {N_Prm[1]} Следующие компоненты:')
                        els_1=list(set([el.split(',')[1]+' '+el.split(',')[6] for el in N1_lst]))
                        els_1.sort()
                        rasklad_nz+=els_1
                        #pprint.pprint(rasklad_nz)
                        FullNameNz=NameDir+'/'+NamePrm+'.txt'
                        with open(FullNameNz, "w",encoding='utf-8') as fprm: 
                            for sp in rasklad_nz:
                                fprm.write(sp)
                                fprm.write('\n')       
                else:
                    print('Указаны отсутствующие в словаре модуля головки-{N_Prm}. Генерация программы установщика PnP прервана.')
        #--------------
        CMDraw.RootLoop()
        #
        return


#======================================================================================================================= Тест ==
    

def main():
    # Получение списка файлов для обработки 
    LAUNCHDIR = 'launch'

    nmodule='B3n2-DC-DC_r1'
    #nmodule='B3n2-ManBot_r1'
    #nmodule='B3n2-ManTop_r1'
    #nmodule='B3n2-LD_r1'
    #nmodule='B3n2-MeasUDiv_r1'
    #nmodule='B3n2-TU_r1'
    spec=CElModule.Pick(nmodule,LAUNCHDIR)
    #spec=CElModule(nmodule,LAUNCHDIR)


    spec.RepSMDprm(0,'F',0,8)
    spec.RepSMDprm(0,'F',0,8,60,True)
    #spec.RepSMDprm(0,'F',90)
    #spec.RepSMDprm(0,'F',180)
    #spec.RepSMDprm(0,'F',270)
    #spec.RepSMDprm(0,'B')
    spec.RepSMDprm(0,'B',0,8)
    spec.RepSMDprm(0,'B',0,8,60,True)
    #spec.RepSMDprm(0,'B',180)
    #spec.RepSMDprm(0,'B',270)
    
    
    #spec.RepSMDprm(0,'B')
    #print(spec.report())
    #print(spec.StdRepIsp(3))
    #print(spec.StdRepIsp(1))
    #print(spec.StdRepIsp(3,10))
    #print(spec.StdRepIsp(0))
    #print(spec.StdRepIsp(2))
    #print(spec.StdRepIsp(0,10))
    
if __name__ == "__main__":
    main()





