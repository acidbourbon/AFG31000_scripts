#!/usr/bin/env python3



import vxi11

import struct
from time import sleep
import numpy as np
import sys
import os
import datetime

from scipy import interpolate

local_objects = {}


def isNaN(num):
    return num != num


def send_data(xdata,ydata,**kwargs):

  trace       = int(kwargs.get("trace",1))
  idle_val    = spice_float(kwargs.get("idle_val",0))
  delay       = spice_float(kwargs.get("delay",0e-9))
  sample_rate = int(spice_float(kwargs.get("sample_rate",2e9)))
  invert      = int(kwargs.get("invert",0))
  
  ip = "192.168.0.203"
  if(os.getenv('AFG31000_IP')):
    ip = os.getenv('AFG31000_IP')
  ip          = str(kwargs.get("ip",ip))
  print("target ip : {}".format(ip))
  
  period      = spice_float(kwargs.get("period",0))
  yscale      = spice_float(kwargs.get("yscale",1))
  xscale      = spice_float(kwargs.get("xscale",1))
  

  
  
  
  
  my_xdata = np.array(xdata)
  my_ydata = np.array(ydata)
  
  session = open_session(ip)

  
  program_trace( my_xdata, my_ydata, 
                     trace       = trace,
                     idle_val    = idle_val,
                     xscale      = xscale,
                     yscale      = yscale,
                     delay       = delay,
                     invert      = invert,
                     sample_rate = sample_rate,
                     period      = period
                  )

  run()
  close_session()



def pulser(**kwargs):

  trace       = int(kwargs.get("trace",1))
  on_val      = spice_float(kwargs.get("on_val",0.5))
  idle_val    = spice_float(kwargs.get("idle_val",0))
  width       = spice_float(kwargs.get("width",50e-9))
  delay       = spice_float(kwargs.get("delay",0e-9))
  sample_rate = int(spice_float(kwargs.get("sample_rate",2e9)))
  invert      = int(kwargs.get("invert",0))
  
  ip = "192.168.0.203"
  if(os.getenv('AFG31000_IP')):
    ip = os.getenv('AFG31000_IP')
  ip          = str(kwargs.get("ip",ip))
  print("target ip : {}".format(ip))
  
  period      = spice_float(kwargs.get("period",0))
  yscale      = spice_float(kwargs.get("yscale",1))
  xscale      = spice_float(kwargs.get("xscale",1))
  
  leading_edge   = spice_float(kwargs.get("leading_edge",0))
  trailing_edge  = spice_float(kwargs.get("trailing_edge",0))

  
  
  #xdata = np.arange(0,width,1./sample_rate)
  #ydata = np.ones(len(xdata))*on_val
  
  delay += leading_edge/2
  
  xlist = []
  ylist = []
  
  xlist += [-leading_edge/2]
  ylist += [idle_val]
  
  xlist += [leading_edge/2]
  ylist += [on_val]
  
  xlist += [width - trailing_edge/2]
  ylist += [on_val]
  
  xlist += [width + trailing_edge/2]
  ylist += [idle_val]
  
  
  xdata = np.array(xlist)
  ydata = np.array(ylist)
  
  session = open_session(ip)

  
  program_trace( xdata, ydata, 
                     trace       = trace,
                     idle_val    = idle_val,
                     xscale      = xscale,
                     yscale      = yscale,
                     delay       = delay,
                     invert      = invert,
                     sample_rate = sample_rate,
                     period      = period
                  )

  run()
  close_session()





def send_csv(**kwargs):

  delimiter   = str(kwargs.get("delimiter",","))
  
  my_file     = str(kwargs.get("file",""))

  trace       = int(kwargs.get("trace",1))
  idle_val    = spice_float(kwargs.get("idle_val",0))
  yscale      = spice_float(kwargs.get("yscale",1))
  xscale      = spice_float(kwargs.get("xscale",1))
  delay       = spice_float(kwargs.get("delay",0e-9))
  sample_rate = int(spice_float(kwargs.get("sample_rate",8e9)))
  invert      = int(kwargs.get("invert",0))
  
  ip = "192.168.0.203"
  if(os.getenv('AWG70002_IP')):
    ip = os.getenv('AWG70002_IP')
  ip          = str(kwargs.get("ip",ip))
  print("target ip : {}".format(ip))
  
  period      = spice_float(kwargs.get("period",0))


  tcol       = int(kwargs.get("tcol","0"))
  ycol       = str(kwargs.get("ycol","1"))
  ch1col     = str(kwargs.get("ch1col",""))
  ch2col     = str(kwargs.get("ch2col",""))
  ch3col     = str(kwargs.get("ch3col",""))
  ch4col     = str(kwargs.get("ch4col",""))

  watch_changes  = int(kwargs.get("watch_changes",0))
  
  
  
  
  
  

  multichan_dic = {}

  if ((ycol != "") and (trace <= 4) and (trace >=1)):
    multichan_dic[trace] = int(ycol)

  if (ch1col != ""):
    multichan_dic[1] = int(ch1col)

  if (ch2col != ""):
    multichan_dic[2] = int(ch2col)

  if (ch3col != ""):
    multichan_dic[3] = int(ch3col)

  if (ch4col != ""):
    multichan_dic[4] = int(ch4col)

  if (len(multichan_dic.keys()) == 0):
    print("I got no signal= argument. Stop.")
    exit()



  
  if (my_file == ""):
    print("no file=<file> argument given")
    exit()

  if (os.path.exists(my_file) == False):
    raise NameError("file {} does not exist!".format(my_file))
    exit()


  last_mod_date = 0

  loop_cntr = 0
  

  while(1):
    
    # get .raw file modification date
    mod_date = os.path.getmtime(my_file)

    if ( mod_date != last_mod_date):
      if (watch_changes):
        print(" ")
        print("csv input file has changed!")

      last_mod_date = mod_date

      session = open_session(ip)


      print("read csv file \"{}\"".format(my_file))
      try:
        data = np.loadtxt(my_file, delimiter=delimiter)
      except:
        raise NameError("sth went wrong while reading csv file \"{}\"".format(my_file))
      finally:
        print("success!")

        
      for trace in multichan_dic.keys():
      
        ch_data_col = multichan_dic[trace]
        print("time data is in csv col {:d}".format(tcol))
        print("ch{:d} data is in csv col {:d}".format(trace,ch_data_col))
        
        xdata = data[:,tcol]*xscale
        xdata += delay
      
        ydata = data[:,ch_data_col]*yscale
        
        print("success!")
        
        program_trace( xdata, ydata, 
                           trace       = trace,
                           idle_val    = idle_val,
                           xscale      = xscale,
                           yscale      = yscale,
                           delay       = delay,
                           invert      = invert,
                           sample_rate = sample_rate,
                           period      = period
                        )



      # done with individual trace stuff

      run()
      close_session()

      if (watch_changes == 0):
        break
      else:
        print ("--------------------------------------------------")
        print ("watching file {}, will reprogram AWG on change ...".format(my_file)) 
        print ("press CTRL+C if you want to abort")

    
    sleep(1) 
    
    # display funny scanning animation
    print(loop_cntr*"_"+"#"+(9-loop_cntr)*"_",end="\r")
    loop_cntr = (loop_cntr +1)%10
  
  




def send_ltspice(**kwargs):
  
  ### suppress STDOUT in this try except block
  old_stdout = sys.stdout
  sys.stdout = open(os.devnull, "w")
  try:
    # use Nuno's PyPi module
    from PyLTSpice.LTSpice_RawRead import RawRead
  except:
    raise NameError("pyltspice module not found. :/\nplease install the pyltspice module via pip\n  sudo pip3 install pyltspice")
  finally:
    sys.stdout.close()
    sys.stdout = old_stdout
  ### end of STDOUT suppression



  my_file     = str(kwargs.get("file",""))
  signal      = str(kwargs.get("signal",""))

  trace       = int(kwargs.get("trace",1))
  idle_val    = spice_float(kwargs.get("idle_val",0))
  yscale      = spice_float(kwargs.get("yscale",1))
  xscale      = spice_float(kwargs.get("xscale",1))
  delay       = spice_float(kwargs.get("delay",0e-9))
  sample_rate = int(spice_float(kwargs.get("sample_rate",8e9)))
  invert      = int(kwargs.get("invert",0))
  
  ip = "192.168.0.203"
  if(os.getenv('AWG70002_IP')):
    ip = os.getenv('AWG70002_IP')
  ip          = str(kwargs.get("ip",ip))
  print("target ip : {}".format(ip))
  
  period      = spice_float(kwargs.get("period",0))


  signal1     = str(kwargs.get("signal1",""))
  signal2     = str(kwargs.get("signal2",""))
  signal3     = str(kwargs.get("signal3",""))
  signal4     = str(kwargs.get("signal4",""))

  watch_changes  = int(kwargs.get("watch_changes",0))
  
  
  
  
  
  

  multichan_dic = {}

  if ((signal != "") and (trace <= 4) and (trace >=1)):
    multichan_dic[trace] = signal

  if (signal1 != ""):
    multichan_dic[1] = signal1 

  if (signal2 != ""):
    multichan_dic[2] = signal2 

  if (signal3 != ""):
    multichan_dic[3] = signal3 

  if (signal4 != ""):
    multichan_dic[4] = signal4 

  if (len(multichan_dic.keys()) == 0):
    print("I got no signal= argument. Stop.")
    exit()



  
  if (my_file == ""):
    print("no file=<file> argument given")
    exit()

  if (os.path.exists(my_file) == False):
    raise NameError("file {} does not exist!".format(my_file))
    exit()


  last_mod_date = 0

  loop_cntr = 0
  while(1):
    
    # get .raw file modification date
    mod_date = os.path.getmtime(my_file)

    if ( mod_date != last_mod_date):
      if (watch_changes):
        print(" ")
        print("LTSpice output has changed!")

      last_mod_date = mod_date

      session = open_session(ip)

      print("read LTSpice binary file \"{}\"".format(my_file))
      try:
        ltr = RawRead(my_file)
      except:
        raise NameError("sth went wrong while reading LTSpice binary file \"{}\"".format(my_file))
      finally:
        print("success!")
        
      for trace in multichan_dic.keys():
      
        signal = multichan_dic[trace]
        
        print("read LTSpice signal \"{}\"...".format(signal))
        
        
        ### suppress STDOUT in this try except block
        old_stdout = sys.stdout
        sys.stdout = open(os.devnull, "w")
        try:
          IR1 = ltr.get_trace(signal)
          x = ltr.get_trace("time") 
                                                                                
          #  #### the abs() is a quick and dirty fix for some strange sign decoding errors
          xdata = abs(x.get_wave(0))
          ydata = IR1.get_wave(0)
        except:
          raise NameError("sth went wrong ... apparently I can't find signal \"{}\" in binary file \"{}\"".format(signal,my_file))
        finally:
          sys.stdout.close()
          sys.stdout = old_stdout
          
       
        print("success!")
        
        program_trace( xdata, ydata, 
                           trace       = trace,
                           idle_val    = idle_val,
                           xscale      = xscale,
                           yscale      = yscale,
                           delay       = delay,
                           invert      = invert,
                           sample_rate = sample_rate,
                           period      = period
                        )



      # done with individual trace stuff

      run()
      close_session()

      if (watch_changes == 0):
        break
      else:
        print ("--------------------------------------------------")
        print ("watching file {}, will reprogram AWG on change ...".format(my_file)) 
        print ("press CTRL+C if you want to abort")

    
    sleep(1) 
    
    # display funny scanning animation
    print(loop_cntr*"_"+"#"+(9-loop_cntr)*"_",end="\r")
    loop_cntr = (loop_cntr +1)%10
  
  





def spice_float(argument):
   
  if( isinstance(argument,str)):
   
    expr = argument
    if("p" in expr):
      expr = expr.replace("p","e-12")
    elif("n" in expr):
      expr = expr.replace("n","e-9")
    elif("u" in expr):
      expr = expr.replace("u","e-6")
    elif("m" in expr):
      expr = expr.replace("m","e-3")
    elif("k" in expr):
      expr = expr.replace("k","e3")
    elif("Meg" in expr):
      expr = expr.replace("Meg","e6")
    elif("M" in expr):
      expr = expr.replace("M","e6")
    elif("G" in expr):
      expr = expr.replace("G","e9")
    elif("T" in expr):
      expr = expr.replace("T","e12")
      
    try:
      number = float(expr)
    except:
      raise NameError("cannot convert \"{}\" to a reasonable number".format(argument))
  else:
    number = float(argument)
  
  return number



  


def resample(target_x,data_x,data_y,**kwargs):
  fill_value = float(kwargs.get("fill_value",0.))
  f = interpolate.interp1d(data_x,data_y,bounds_error=False, fill_value=fill_value)
  out_x = target_x
  out_y = f(target_x)
  return (out_x,out_y)


def open_session(ip):
  
  # Open socket, create waveform, send data, read back and close socket
  print("connect to device ...")
  session = vxi11.Instrument('TCPIP::{}::INSTR'.format(ip))
  session.timeout = 500
  session.clear()
  #session.chunk_size = 102400
  print("*IDN?")
  idn_str = session.ask("*idn?")
  print(idn_str)
  if( "TEKTRONIX,AFG31" in idn_str):
    print("success!")
  else:
    session.close()
    raise NameError("could not communicate with device, or not a Tektronix AFG31000")
  local_objects["session"] = session
  return session
  


def close_session():
  if (not("session" in local_objects.keys())):
    raise NameError("there is no running communication session with AWG!")
  session = local_objects["session"]
  
  print("close socket")
  session.close()
  
def __del__(self):
  close_session()
  
  
  
def run():
  return 0
  #if (not("session" in local_objects.keys())):
  #  raise NameError("there is no running communication session with AWG!")
  #session = local_objects["session"]
# 
#  print("RUN!")
#  session.write("AWGControl:RUN")

  
  
def stop():
  return 0
  #if (not("session" in local_objects.keys())):
  #  raise NameError("there is no running communication session with AWG!")
  #session = local_objects["session"]
# 
#  print("STOP!")
#  session.write("AWGControl:STOP")
  #session.write("OUTPUT1:STATE 0")
  #session.write("OUTPUT2:STATE 0")
  
 
  

def next_int_mult_128(n):
  return np.max([int((n)/128+1)*128,128]) # multiples of 128


def prev_int_mult_128(n):
  return np.max([int((n)/128)*128,128]) # multiples of 128

  
def program_trace(xdata,ydata,**kwargs):
  
  #stop()
  
  if (not("session" in local_objects.keys())):
    raise NameError("there is no running communication session with AWG!")
  session = local_objects["session"]
  
  
  
  MIN_SAMPLE_LEN = 2000
  #MIN_SAMPLE_LEN = 1024
  
  
  trace       = int(kwargs.get("trace",1))
  idle_val    = float(kwargs.get("idle_val",0))
  yscale      = float(kwargs.get("yscale",1))
  xscale      = float(kwargs.get("xscale",1))
  delay       = float(kwargs.get("delay",0e-9))
  sample_rate = int(float(kwargs.get("sample_rate",2e9)))
  invert      = int(kwargs.get("invert",0))
  period      = float(kwargs.get("period",0))
    
  print("idle val: {}".format(idle_val))

  
  
  print("preparing data for channel {:d}".format(trace))
  
  
  xdata = xdata*xscale + delay

  width = xdata[-1]

  ydata = ydata*yscale

    

  target_x = np.arange(0,width,1./sample_rate)
  target_x , target_y = resample(target_x,xdata,ydata,fill_value=idle_val)
    
  if( np.max(np.abs(target_y)) > 2.5):
    print("############################################")
    print("## WARNING: Waveform on ch {:d} will clip!!! ##".format(trace))
    print("############################################")
    
  target_y[target_y > 2.5] = 2.5
  target_y[target_y < -2.5] = -2.5
    
  if(invert):
    idle_val = -idle_val
    target_y = -target_y
    
  ymin = np.min(target_y)
  ymax = np.max(target_y)
  ypp  = ymax-ymin
  amplitude = ypp
  offset = (ymin+ymax)/2.

  target_y -= ymin
  target_y /= ypp
  target_y *= 2**14-1
  
  # need to transform idle val as well!
  # you are a dumb dumb!
  idle_val -= ymin
  idle_val /= ypp
  idle_val *= 2**14-1
   
  



  #target_y = target_y/.25
  #idle_val = idle_val/.25





  n = int(len(target_x))
  
  freq=0
  
  sample_len = 0
  if(period == 0):
    #sample_len = np.max([MIN_SAMPLE_LEN,n])
    period = width
    freq=1/(width)
  else:
    freq=1/period
    # the min sample length is controlled via sample_multiplier
  
  sample_len = int(period * sample_rate)
  
  dataList = idle_val*np.ones(sample_len)
  
  n_ = np.min([n,sample_len])
  
  dataList[0:n_] = target_y[0:n_]
  
  #send data
  print("sending data ...")

  
  substring = ""
  datastring = ""
  data = bytearray()
  

  waveform_length = sample_len # * sample_multiplier
  print("waveform length: {:d}".format(waveform_length))
  print("sample length: {:d}".format(sample_len))

  for i in range(sample_len):
        
    value = 0
    if not(isNaN(dataList[i])):
      value = int(dataList[i])
    if value<0:
      value = 0
    data += bytearray(struct.pack(">H", value))
    
    
  session.write("SOURCE{:d}:FUNCTION EMEM{:d}".format(trace,trace))
  session.write("SOURCE{:d}:FREQUENCY {:3.3e}".format(trace,freq))

  session.write("SOURCE{:d}:VOLTAGE:AMPLITUDE {:1.3f}".format(trace,amplitude))
  session.write("SOURCE{:d}:VOLTAGE:OFFSET {:1.3f}".format(trace,offset))
    
  commandString = "TRACE:DATA EMEM{:d}, #{}{}".format(trace,len(str(2*waveform_length)), str(2*waveform_length))# + datastring

  session.write_raw( str.encode(commandString) + data )

  session.write("OUTPUT{:d}:STATE 1".format(trace))

  
  
