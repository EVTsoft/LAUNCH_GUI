import math

class CXY():

  def __init__(self,x=0.,y=0.):
      self.__x=x
      self.__y=y


  def copy(self):
      return CXY(self.__x,self.__y)


  def norm(self,cxy):
      self.__x=round(self.__x-cxy.x,6)
      self.__y=round(self.__y-cxy.y,6)
      return self


  def newnorm(self,cxy):
      return self-cxy      


  def norm_round(self,cxy,rnd=7):
      xy=self.newnorm(cxy)
      return CXY(round(xy.x,rnd), round(xy.y,rnd))
    

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
  #@x.setter
  def set_x(self, ix):
    self.__x=ix  
  
  @property
  def y(self):
    return self.__y
  #@y.setter
  def set_y(self, iy):
    self.__y=iy  
  


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
    def scale(self):
        return self.__scale
    

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
    
    
    @property
    def side(self):
        return self.__side
    
    
    def size(self,sc):
        x=self.__brd.x
        y=self.__brd.y
        if (self.__angle==90) | (self.__angle==270):
            x=self.__brd.y
            y=self.__brd.x
        return f'{round(sc*self.__scale*x)}x{round(sc*self.__scale*y)}'    


    def tr_angle(self,ang):
        ret_angle=(ang+self.__angle)%360
        if self.__side=='B':
            ret_angle=(360-((360+self.__angle-ang)%360))%360
        return ret_angle
       
    def tr_nscale(self,xy):
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
        return CXY(x,y)           


    def tr(self,ixy):
        xy=self.tr_nscale(ixy)                 
        x=round(xy.x*self.__scale)   
        y=round(xy.y*self.__scale)   
        return CXY(x,y)           
    
    def tr_plt_nscale(self,ixy,rnd=7):
        xy=self.tr_nscale(ixy)
        x=round(xy.x,rnd)   
        y=round(self.__brd.y-xy.y,rnd)   
        return CXY(x,y)           
    

    def lvector(self,xy,lny=True):
        #print (xy)
        XY=self.tr(xy)
        x=0
        y=self.__brd.y
        if (self.__angle==90) |(self.__angle==270):
            y=self.__brd.x 
        x=round(x*self.__scale)   
        y=round(y*self.__scale)       
        x=XY.x-x    
        y=XY.y-y 
        r=math.sqrt(x**2+y**2)   
        #print (xy,'  ',XY,'  ',r,'  ',x,'  ',y)
        return r


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
