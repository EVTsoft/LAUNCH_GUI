# -*- coding: utf-8 -*-
"""Модуль сканирует BOM."""
import pprint
import os
import re
import json
from CElModule import CElModule
from CSpecification import CSpecification
import pprint

LISPN=40

class CLaunch:
    def __init__(self,nfo,ndirmod='launch'):
        self.__mod_bom = []        # для каждого файла запуска обнуляем список входящих в него модулей
        self.__launch_spec = {}
        self.__launch_fn=nfo
        self.__launch_dir=ndirmod
        if '.zap' in self.__launch_fn : 
            print(f'\n\n\n>>>Запуск: {self.__launch_fn}')
            with open(self.__launch_fn,'r',encoding="utf-16") as json_file:
                self.__mod_bom = json.load(json_file)   #  Считали запуск
                self.__launch_spec=CSpecification()
                for modul in self.__mod_bom:
                    mod=CElModule.Pick(modul['bommod'],self.__launch_dir)
                    dm_isp=modul['mtypes']
                    for m_isp in dm_isp:
                        print(f' исполнение: {m_isp['var']}  штук: {m_isp['quantity']}'.ljust(30),end='')
                        sp=mod.GetIsp(int(m_isp['var']),int(m_isp['quantity']))
                        m_isp['spec']=sp
                        self.__launch_spec=self.__launch_spec+sp
                print(' ')


    @property
    def mod_bom(self):
        return self.__mod_bom
    
    
    @property
    def launch_fn(self):
        return self.__launch_fn
    

    @property
    def launch_dir(self):
        return self.__launch_dir
    
    
    @property
    def launch_spec(self):
        return self.__launch_spec
    

    def spmod_ai(self,mod):
        spm=CSpecification()
        for sisp in mod['mtypes']:spm+=sisp['spec']
        return spm

    def strmod_ai(self,mod):
        sret='\n'
        sret+=f'{mod['bommod'].ljust(17)}'
        for sisp in mod['mtypes']:sret+=f'  >>исп.-{sisp['var']} ~ шт.:{sisp['quantity']}   '
        return sret
    
    def rpt(self):
        return f'\n\n ================ Полная спецификация запуска {self.__launch_fn}: \n'+self.__launch_spec.repstd()  
    
    def rpt_allMS(self,fun=lambda sp,m: sp.spmod_ai(m).repstd()):
        sret=f'\n\n ================ Помодульная спецификация.        Запуск: {self.__launch_fn}:\n'
        for mod in self.__mod_bom:
            sret+=self.strmod_ai(mod)+'\n'
            sret+=fun(self,mod)+'\n'
        return sret

     
    def rpt_SMD_pack(self):
        sret=f'\n\n ================ Разбивка SMD компонент по типу упаковки.        Запуск: {self.__launch_fn}:\n' \
              +self.__launch_spec.rep_SMD_pack()+'\n'
        sret+= self.rpt_allMS(lambda sp,m: sp.spmod_ai(m).rep_SMD_pack())  
        return sret
    
    def rpt_stanoks(self):
        stns=list(set([ m['Stanok'] for m in self.__mod_bom]))
        stns.sort()
        spsts=dict.fromkeys(stns)
        for s in stns: spsts[s]=[CSpecification(),'']
        for mod in self.__mod_bom:
            spsts[mod['Stanok']][0]+=self.spmod_ai(mod)
            spsts[mod['Stanok']][1]+=self.strmod_ai(mod)
        sret=''
        for st in stns:
            sret+=f'\n\n Станок №{st}: ==============================================================================================================================================' \
                                                              +spsts[st][1]+'\n' + \
'\nI.   Питатели 8мм с 1 по 30 (левая сторона):\n'            +spsts[st][0].rep_SMD_pack(('tape8',),True,'RCL') +\
'\nII.  Питатели 8мм с 31 по 40 (правая сторона):\n'          +spsts[st][0].rep_SMD_pack(('tape8',),True,'EC') +\
'\nIII. Оставшиеся питатели с 41 по 54 (правая сторона):\n'   +spsts[st][0].rep_SMD_pack(('tape12','tape16','tape24'),True,'ALL') + \
'\nIV.  Следующие электронные компоненты необходимо разместить в палете:\n'+spsts[st][0].rep_SMD_pack(('tray','tube','misc.','tape32','tape88'),True,'ALL')
        sret+='\n'    
        return sret

def main():
    cz=CLaunch('zapusk_B3n2_2000.zap') 
    #cz=CLaunch('zapusk_00.zap') 
    #cz=CLaunch('zapusk_01.zap') 
    #cz=CLaunch('zapusk_010.zap') 
    #cz=CLaunch('zapusk_011.zap') 
    #cz=CLaunch('zapusk_02.zap') 
    #cz=CLaunch('zapusk_03.zap') 
    #cz=CLaunch('zapusk_01.zap')
    #print('\n')


    #print(cz.rpt())
    #print(cz.rpt_allMS())
    #print(cz.rpt_SMD_pack())
    #print(cz.rpt_stanoks())
    pprint.pprint(cz.launch_spec)
    pprint.pprint(cz.mod_bom)
    pprint.pprint(cz.launch_dir)
    pprint.pprint(cz.launch_fn)
    
    #print(cz.rpt_SMDRLC_pack8(1))
    #print(cz.rpt_SMDRLC_pack8(2))
    #print(cz.rpt_SMDRLC_pack8(3))
    #print(cz.rpt_SMDRLC_pack8(4))
    #print (cz.rpt_correlation())


if __name__ == "__main__":
    main()

