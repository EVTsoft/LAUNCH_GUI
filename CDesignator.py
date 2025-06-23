 
class CDesignator():

    def __init__(self,iDes,iLayer,iAngle,iXY,iXY1p) : 
        self.__Des=iDes
        self.__Layer=iLayer
        self.__Angle=iAngle
        self.__XY=iXY
        self.__XY1p=iXY1p
    
    @property
    def Layer(self):
        return self.__Layer
    
    @property
    def XY1p(self):
        return self.__XY1p
    
    @property
    def Des(self):
        return self.__Des
    
    @property
    def XY(self):
        return self.__XY
    
    @property
    def Angle(self):
        if(self.__Layer=='F'):
            return self.__Angle
        else:
            return (540.-self.__Angle)%360.
  

    def __str__(self):
        return f' {self.__Des:>6}     {self.__Layer}     {self.__Angle:3}    {self.__XY}   {self.__XY1p} '
     