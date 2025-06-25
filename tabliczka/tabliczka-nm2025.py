#!/usr/bin/python
# coding: utf-8

import sys, os, csv, re, yaml
from datetime import datetime
sys.path.append("..")
FPDF_FONT_DIR='/home/tomek/Dokumenta/Priv/Klub/Tabliczka'
SYSTEM_TTFONTS='/home/tomek/Dokumenta/Priv/Klub/Tabliczka'

import fpdf,collections

def input_time(times):
  fmt = '%H:%M'
  d1 = datetime.strptime(times,fmt)
  return d1.minute
#  return int(d1.minutes)

def obrob_przystanki(item,count,x,y):
#  print "COUNT" + str(count)
  przystanki_count=len(item)
  czas_od=0
  yshift=0
  odstep=cfg['przystanki']['odstep']
  output = ''
  for i in range(0,count):
    [status,przystanek,czas,h]=item[i]
    m = re.split("\[", przystanek)
    s = m[0].rstrip()
    pdf.text(x+6,y+yshift,s)
    yshift = yshift+odstep
  for i in range(count,przystanki_count):
    [status,przystanek,czas,h]=item[i]
    idx = (i + 1) % len(item)
    [next_status,next_przystanek,next_czas,htest]=item[idx]
    pdf.text(x,y+yshift,str(czas_od))
    czas_od=input_time(next_czas)+czas_od
    m = re.split("\[", przystanek)
    s = m[0].rstrip()
    
#    print "PRZYST"
#    print s
    status_width=pdf.get_string_width(status)

    try:
      m[1]
    except IndexError:
      pdf.text(x+6,y+yshift,m[0])
      if status != 'hidden':
        pdf.text(x+66-status_width,y+yshift,status)
      pdf.line(x+5,y+yshift-odstep,x+5,y+yshift)
      yshift=yshift+odstep
    else:
      pdf.text(x+6,y+yshift,m[0])
      if status != 'hidden':
        pdf.text(x+76-status_width,y+yshift,status)
      pdf.line(x+5,y+yshift-odstep,x+5,y+yshift)
      pdf.set_font('Roboto','B',6)
      newstr = m[1].replace("]", "")
      pdf.text(x+6,y+yshift+3,newstr)
      pdf.set_font('Roboto','',7)
      yshift=yshift+odstep + 3
    
def obrob_odjazdy(lista_odjazdow,index,x,y):
  yshift=0

  godzinowo = {}
  global starting_hour
  for odjazdy in lista_odjazdow:
    [odjazd,oznaczenie]=odjazdy
    [godzina,minuta]=odjazd.split(":")
    godzina=int(godzina)
    godzinowo.setdefault(godzina,[]).append([minuta,oznaczenie])

  od = collections.OrderedDict(sorted(godzinowo.iteritems()))
  
#  print od
  busio = 0
  
  for i,v in od.iteritems():
    
    if starting_hour is None:
      starting_hour = i
    i=int(i)
    printedi=i
    if i > 23 and busio == 0:
      pdf.set_font('Roboto','B',8)
      pdf.text(x,y+yshift*6,'Następny dzień')
      pdf.line(x-2,y+yshift*6+2,x+58,y+yshift*6+2)
      yshift=yshift+1
      printedi=i-24
      busio=1    
    pdf.set_font('Roboto','B',8)
    pdf.text(x,y+yshift*6,str(printedi))
    pdf.line(x+6,y+yshift*6-4,x+6,y+yshift*6+2)
    pdf.line(x-2,y+yshift*6+2,x+68,y+yshift*6+2)

    z = 1
    for j in od.get(i,''):          
          pdf.set_font('Roboto','',8)
          pdf.text(x+(z*8),y+yshift*6,str(j[0])+str(j[1]))
          pdf.line(150,y+yshift*6-4,150,y+yshift*6+2)          
          legenda_indexes.extend(list(j[1]))
          z = z + 1
    yshift=yshift+1


def obrob_legende(text,x,y):
#  legenda=text.split(";")
  pdf.set_xy(x,y)
  texttoprint = ''
  try:
    texttoprint += legenda['boldtext'].encode('utf-8') + "\n"
  except:
    print "nie ma megatestu"
  
  d = collections.OrderedDict(sorted(legenda.items()))
  for i in d:
      #print i in legenda_indexes
      if i in legenda_indexes:
        texttoprint += str(i) + " - " + legenda[i].encode('utf-8') + "\n"
      elif i.find("text") != -1:
        texttoprint += legenda[i].encode('utf-8') + "\n"
  pdf.multi_cell(100,3.5,texttoprint)


pdf = fpdf.FPDF('P','mm','A4')
pdf.add_font('Roboto', '', 'RobotoCondensed-Regular.ttf', uni=True)
pdf.add_font('Roboto', 'B', 'RobotoCondensed-Bold.ttf', uni=True)
pdf.add_page();


with open(sys.argv[1], "r") as ymlfile:
    cfg = yaml.load(ymlfile)

#print cfg

j = 0

#odsunięcie rozkładu
starty=cfg['tabela']['odsuniecie']

#napisy
napis_a=cfg['napisy']['a']
napis_id=cfg['napisy']['id']
napis_b=cfg['napisy']['b']
napis_c=cfg['napisy']['c']
napis_d=cfg['napisy']['d']

schema_path=cfg['schema_path']
filename = cfg['filename'];
try:
  line_number = cfg['linenumber']
except:
  print "Numer linii jest pusty"

try:
  line_logo = cfg['linelogo']
except:
  print "Logo linii jest puste"
  
legenda = cfg['legenda']

odjazdy = {}
legenda_indexes = przystanki = []
b = []
tia = []
p = re.compile('(\d)?\d:\d\d')

with open(filename, 'rb') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for r in spamreader:
        tia.append(r) 

row_count=len(tia)
objasnienia=tia[0]
#print "OBJASNIENIA"
#print objasnienia

for r in range(1,row_count):
    row = tia[r]
    print "Przystanki"
    print row
    przystanki.append([row[0],row[1],row[4],row[6]])
    my_list_len = len(row)
    for z in range(6,my_list_len):
        if(p.match(row[z])):            
             b.append([row[z],objasnienia[z]])            
    odjazdy[row[6]]=b
    b = []        




for [k,i,z,h] in przystanki:
  if k != 'hidden':
  #print "PRZYSTANEK: "+h
    starting_hour=None
    legenda_indexes = []
    pdf.image(schema_path,0,0,210,297);

    pdf.line(cfg['tabela']['margines_lewy'],starty,cfg['tabela']['margines_lewy']+190,starty)
    pdf.line(cfg['tabela']['margines_lewy'],starty,cfg['tabela']['margines_lewy'],starty+cfg['tabela']['wysokosc'])
    pdf.line(cfg['tabela']['margines_lewy'],starty+cfg['tabela']['wysokosc'],200,starty+cfg['tabela']['wysokosc'])
    pdf.line(cfg['tabela']['margines_lewy']+190,starty,cfg['tabela']['margines_lewy']+190,starty+cfg['tabela']['wysokosc'])

    pdf.line(cfg['tabela']['margines_lewy']+70,starty,cfg['tabela']['margines_lewy']+70,starty+cfg['tabela']['wysokosc'])
    pdf.line(cfg['tabela']['margines_lewy'],starty+32,cfg['tabela']['margines_lewy']+70,starty+32)

    pdf.line(cfg['tabela']['margines_lewy']+70,starty+15,cfg['tabela']['margines_lewy']+190,starty+15)
    pdf.line(cfg['tabela']['margines_lewy']+70,starty+22,cfg['tabela']['margines_lewy']+140,starty+22)
    
# te -45 można by liczyć na podstawie wielkości legendy

    pdf.line(cfg['tabela']['margines_lewy']+140,starty+15,cfg['tabela']['margines_lewy']+140,starty+cfg['tabela']['wysokosc']-35)
    pdf.line(cfg['tabela']['margines_lewy']+70,starty+cfg['tabela']['wysokosc']-35,cfg['tabela']['margines_lewy']+190,starty+cfg['tabela']['wysokosc']-35)
    pdf.line(cfg['tabela']['margines_lewy']+70,starty+cfg['tabela']['wysokosc']-10,cfg['tabela']['margines_lewy']+190,starty+cfg['tabela']['wysokosc']-10)


    pdf.set_font('Roboto','',6)
    pdf.text(cfg['tabela']['margines_lewy']+72,starty+cfg['tabela']['wysokosc']-2,'Tramwaje i autobusy zabytkowe na każdą okazję!')
    
#    pdf.image('../10-lat-klub_mini.png',cfg['tabela']['margines_lewy']+82,starty+cfg['tabela']['wysokosc']-8.5,21,7)

    pdf.set_font('Roboto','B',8)
    pdf.text(cfg['tabela']['margines_lewy']+169,starty+cfg['tabela']['wysokosc']-2,'http://kstm.pl')

  
#linia specjalna i numer linii
    pdf.set_font('Roboto','',8)
    napis_width=pdf.get_string_width(napis_a)
    pdf.text(cfg['tabela']['margines_lewy']+35-napis_width/2,starty+5,napis_a)
  
    pdf.set_font('Arial','B',55)
    try:
#      line_str=str(line_number)
#      print line_str
      napis_width=pdf.get_string_width(str(line_number))
#      print line_number
      pdf.text(cfg['tabela']['margines_lewy']+35-napis_width/2,starty+25,line_number)
    except Exception as e:
      print e 
      print "Nie znaleziono numeru linii"
    
    try:
      pdf.image(line_logo,cfg['tabela']['margines_lewy']+28,starty+6,25,25)
    except:
      print "Nie ma logo linii lub nie udało się odczytać pliku"
  
#kprzystanek 
    pdf.set_font('Roboto','',10)
    przyst=re.split("\[",i)
    if len(k) > 0:
      status_t = ' ('+k+')'
    else:
      status_t = ''
    pdf.set_xy(cfg['tabela']['margines_lewy']+71,starty+1)    
    pdf.multi_cell(100,4,'PRZYSTANEK: '+przyst[0]+status_t+" ("+h+")",0,'L')
  
    pdf.set_font('Roboto','',6)
    pdf.text(185,starty+2,napis_id)
  
#info o rozkladzie
    pdf.set_font('Roboto','B',8)
    napis_bt=napis_b.split("#")
    dlugosc_y=len(napis_bt)+1
    y_t = 0
    for napis_best in napis_bt:
      pdf.text(cfg['tabela']['margines_lewy']+cfg['napisy']['b_adjust'],starty+13-dlugosc_y+y_t*2.5,napis_best)
      y_t = y_t + 1
    pdf.set_font('Roboto','',7)

#  print j
#przystanki
    pdf.text(10.5,starty+37,'CZAS')
    pdf.text(18,starty+37,'PRZYSTANEK')
  
    obrob_przystanki(przystanki,j,cfg['tabela']['margines_lewy']+2,starty+42)

# godziny odjazdow

#  print odjazdy[i]
    print odjazdy[h]
    pdf.set_font('Arial','B',8)
    obrob_odjazdy(odjazdy[h],i,82,starty+26)

# rozklad wazny
    pdf.set_font('Roboto','B',12)
    pdf.text(cfg['tabela']['margines_lewy']+105-pdf.get_string_width(napis_c)/2,starty+20,napis_c)
    
    pdf.set_font('Roboto','',7)
    if legenda is not None:
      obrob_legende(legenda,cfg['tabela']['margines_lewy']+71,starty+cfg['tabela']['wysokosc']-35)

    if cfg['logo']['kstm_big'] == 1:
      pdf.image('kstm_logo.png',150,starty+20,40,40)
      pdf.set_font('Roboto','B',6)
      pdf.text(cfg['tabela']['margines_lewy']+142,starty+cfg['tabela']['wysokosc']-43,'Linię obsługuje:')
      pdf.text(cfg['tabela']['margines_lewy']+142,starty+cfg['tabela']['wysokosc']-40,'Klub Sympatyków Transportu Miejskiego')
      pdf.text(cfg['tabela']['margines_lewy']+142,starty+cfg['tabela']['wysokosc']-37,'http://kstm.pl')

    if cfg['logo']['kstm'] == 1:
      pdf.set_font('Roboto','B',6)
      pdf.text(cfg['tabela']['margines_lewy']+153,starty+18,'Linię obsługuje:')
      pdf.text(cfg['tabela']['margines_lewy']+153,starty+21,'Klub Sympatyków Transportu Miejskiego')
      pdf.text(cfg['tabela']['margines_lewy']+153,starty+24,'http://kstm.pl')
      pdf.image('kstm_logo.png',cfg['tabela']['margines_lewy']+140,starty+16,12,12)

  
    pdf.set_font('Roboto','B',8)
    pdf.set_xy(cfg['tabela']['margines_lewy']+141,starty+17)
    pdf.multi_cell(46,3.5,napis_d)
    try:
      if cfg['logo']['mpk'] == 1:
        pdf.image('logo_mpkwroclaw.png',cfg['tabela']['margines_lewy']+144,starty+50,45,12)

      if cfg['logo']['tmw'] == 1:
        pdf.image('tmw.png',cfg['tabela']['margines_lewy']+144,starty+70,40,40)
      if cfg['logo']['qr'] == 1:
        try:
          pdf.image(cfg['logo']['qr_path'],cfg['tabela']['margines_lewy']+144,starty+cfg['tabela']['wysokosc']-80,40,40)
        except:
          pdf.image('qr.png',cfg['tabela']['margines_lewy']+144,starty+cfg['tabela']['wysokosc']-80,40,40)

        pdf.set_font('Roboto','',7)
        pdf.set_xy(cfg['tabela']['margines_lewy']+141,starty+cfg['tabela']['wysokosc']-87)
        pdf.multi_cell(46,3.5,cfg['napisy']['e'])
        pdf.set_font('Roboto','B',6)
        pdf.text(cfg['tabela']['margines_lewy']+142,starty+cfg['tabela']['wysokosc']-38,cfg['napisy']['f'])
    except KeyError:
      print "oj nie będzie"  
  
    pdf.set_font('Roboto','',6)
    pdf.set_x(230)
    pdf.set_y(237)
    
    pdf.add_page()
  j=j+1  

try:
  pdf.output(r"./"+cfg['output'],"F")
except KeyError:
  pdf.output(r"./invoice.pdf","F")
