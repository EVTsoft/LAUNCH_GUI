import math

class CXY():

  def __init__(self,x=0.,y=0.):
      self.__x=x
      self.__y=y


  def lvector(self,side,xy,size_xy,lny=True):
    x=0.
    if side=='F':
        x=self.__x
    else:
        x=size_xy.x-self.__x 
    y=0
    if lny:
        y=self.__y  
    else:
        y=size_xy.y-self.__y
    x=x-xy.x    
    y=y-xy.y    
    return math.sqrt(x**2+y**2)


  def copy(self):
      return CXY(self.__x,self.__y)


  def norm(self,cxy):
      self.__x=round(self.__x-cxy.x,6)
      self.__y=round(self.__y-cxy.y,6)
      return self


  def newnorm(self,cxy):
      return self-cxy      


  def min(self,cxy):
      if self.__x > cxy.x : self.__x=cxy.x
      if self.__y > cxy.y : self.__y=cxy.y
      return self
 

  def max(self,cxy):
      if self.__x < cxy.x : self.__x=cxy.x
      if self.__y < cxy.y : self.__y=cxy.y
      return self
      
      

  def __mul__(self,value):
      return CXY(self.x*value,self.y*value)


  def __imul__(self,value):
      self.__x*=value
      self.__y*=value
      return self
  
  def __truediv__(self,value):
      return CXY(round(self.x/value,6),round(self.y/value,6))

  def __itruediv__(self,value):
      self.__x/=value
      self.__y/=value
      return self

  def __add__(self,value):
      return CXY(self.x+value.x,self.y+value.y)

  def __iadd__(self,value):
      self.__x+=value.x
      self.__y+=value.y
      return self

  def __sub__(self,value):
      return CXY(self.x-value.x,self.y-value.y)

  def __isub__(self,value):
      self.__x-=value.x
      self.__y-=value.y
      return self

  def __eq__(self, value):
    return (value.x==self.__x) & (value.y==self.__y) 

  def __str__(self):
    return f'  x={self.__x: 6.2f}  y={self.__y: 6.2f}'
  
  def __hash__(self):
    return hash(str(self))

  @property
  def x(self):
    return self.__x
  @property
  def y(self):
    return self.__y
  


class tCXY():
    def __init__(self,scale,brd,side,angle):
        self.__scale=scale
        self.__brd=brd
        self.__side=side
        self.__angle=angle

    
    @property
    def brd(self):
        return self.__brd
    

    @property
    def width(self):
        x=self.__brd.x
        if (self.__angle==90) | (self.__angle==270):
            x=self.__brd.y
        return round(self.__scale*x)
    

    @property
    def height(self):
        y=self.__brd.y
        if (self.__angle==90) | (self.__angle==270):
            y=self.__brd.x
        return round(self.__scale*y)
    

    @property
    def angle(self):
        return self.__angle
    
    
    def size(self,sc):
        x=self.__brd.x
        y=self.__brd.y
        if (self.__angle==90) | (self.__angle==270):
            x=self.__brd.y
            y=self.__brd.x
        return f'{round(sc*self.__scale*x)}x{round(sc*self.__scale*y)}'    
    

    def tr(self,xy):
        x=0
        y=0
        if(self.__side=='F'):
            match self.__angle:
                case 0:
                    x=xy.x
                    y=self.__brd.y-xy.y
                case 90:
                    x=self.__brd.y-xy.y
                    y=self.__brd.x-xy.x
                case 180:
                    x=self.__brd.x-xy.x
                    y=xy.y
                case 270:
                    x=xy.y
                    y=xy.x
                case _:
                    print('ВНИМАНИЕ! Ошибка угла поворота платы side F *********************************')  
        else:
             match self.__angle:
                case 0:
                    x=self.__brd.x-xy.x
                    y=self.__brd.y-xy.y
                case 90:
                    x=xy.y
                    y=self.__brd.x-xy.x
                case 180:
                    x=xy.x
                    y=xy.y
                case 270:
                    x=self.__brd.y-xy.y
                    y=xy.x
                case _:
                    print('ВНИМАНИЕ! Ошибка угла поворота платы side B *********************************')                 
        x=round(x*self.__scale)   
        y=round(y*self.__scale)   
        return CXY(x,y)           


    def trvl(self,Txy,half,angle=0):
        xy=None
        if((angle==90) | (angle==270)):
            xy=CXY(Txy.x-half.y,Txy.y+half.x)
        else:
            xy=CXY(Txy.x-half.x,Txy.y+half.y)
        return self.tr(xy)
    

    def trnp(self,Txy,half,angle=0):
        xy=None
        if((angle==90) | (angle==270)):
            xy=CXY(Txy.x+half.y,Txy.y-half.x)
        else:
            xy=CXY(Txy.x+half.x,Txy.y-half.y)
        return self.tr(xy)
    

  
def main():
  a=CXY(20.,100.)
  b=CXY(30.,500.)
  c=CXY(3.,2.)
  print('      a=',a)
  print('      b=',b)
  print('      c=',c)
  print('    a-b=',a-b)
  print('    a+b=',a+b)
  print('    a*c=',a*c)
  print('    b/c=',b/c)
  a*=c
  b/=c
  print('a*=c  a=',a)
  print('b/=c  b=',b)
  
  


if __name__ == "__main__":
  main()
