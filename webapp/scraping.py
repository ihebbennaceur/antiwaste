def linkpls():
  links=[]
  h=['1','2','3','4','5']
  links2=[]
  for i in alphabet:
    links.append(f'https://www.marmiton.org/recettes/index/ingredient/{i}/') 
  links2=[]
  for i2 in range(len(links)):
    for z in h:
      links2.append(links[i2]+z)
  return links2        

new=[]
for lien in linkpls():
  r2=requests.get(lien)
  r2.text[0:200]
    # Instanciate BeautifulSoup class
  soup2=BeautifulSoup( r2.text, "html.parser") # Here we used an HTML Parser
  hello=soup2.find_all('div',attrs={'class':"index-item-card-name"})
  listscraped=[]
  for k in range(len(hello)):
    # print((str(hello[k]).split('">')[1].split('<')[0]))
    listscraped.append(str(hello[k]).split('">')[1].split('<')[0])
    len(listscraped)
    l2=[]
    # new=[]
    for x in listscraped :
      l2.append(x.split("\t"))
    for t in range(len(l2)):  
      new.append(l2[t][4] )
    print(new) 
new=np.unique(new)
df=pd.DataFrame()
df["compo"]=list(new)
df
  