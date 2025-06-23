import math

class CXY():

  def vl(self,half,angle=0):
    xy=None
    if((angle==90) | (angle==270)):
        xy=CXY(self.x-half.y,self.y+half.x)
    else:
        xy=CXY(self.x-half.x,self.y+half.y)
    return xy
  
  def np(self,half,angle=0):
    xy=None
    if((angle==90) | (angle==270)):
        xy=CXY(self.x+half.y,self.y-half.x)
    else:
        xy=CXY(self.x+half.x,self.y-half.y)
    return xy

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

    def tr(self,xy):
        y=round((self.__brd.y-xy.y)*self.__scale)
        if self.__side=='F':
           x=xy.x
        else:
           x=self.__brd.x-xy.x
        x=round(x*self.__scale)   
        return CXY(x,y)           

    @property
    def brd(self):
        return self.__brd
    

    @property
    def width(self):
        return round(self.__scale*self.__brd.x)
    

    @property
    def height(self):
        return round(self.__scale*self.__brd.y)
    
    
    def size(self,sc):
     return f'{round(sc*self.__scale*self.__brd.x)}x{round(sc*self.__scale*self.__brd.y)}'        

  
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
