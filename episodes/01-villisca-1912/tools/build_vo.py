import re
src=open('villisca_vo_source.txt').read()
ph=[("Villisca","vih-LISS-kuh"),("Stillinger","STILL-ing-er"),("Peckham","PECK-um"),("Epperly","EP-er-lee"),("Wilkerson","WILL-ker-sun"),("Mansfield","MANZ-feeld"),("Landers","LAN-derz"),("Lyn George","Lin George"),("Logan","LOW-gun"),("Horton","HOR-tun"),("Boyd","Boyd"),("Retta","RET-uh"),("Lena","LEE-nuh"),("Ina","EYE-nuh"),("Moore","MORE"),("Moores","MORES"),("Landers's","LAN-derz-iz"),("Lyn","Lin")]
def phon(t):
    for a,b in sorted(ph,key=lambda x:-len(x[0])): t=re.sub(r'\b'+a+r'\b',b,t)
    return t
chunks=re.split(r'=== CHUNK (\d+) ===\n',src)[1:]
sil={'03':5,'07':5,'09':5,'10':5}
wpm=137; t=0; rows=[]; tw=0
v3=[];v2=[]
for n,body in zip(chunks[0::2],chunks[1::2]):
    body=body.strip()
    plain=re.sub(r'\[[^\]]+\]','',body)
    w=len(re.findall(r"[A-Za-z0-9'\-]+",plain))
    p=body.count('[pause]')*1.5+body.count('...')*0.8
    lines=len(body.splitlines())
    dur=w/wpm*60+p+sil.get(n,0)
    rows.append((n,w,lines,int(t),round(dur,1)))
    t+=dur;tw+=w
    v3.append(f"=== CHUNK {n} (do not paste this line) ===\n{phon(body)}")
    b=phon(body).replace('[pause]\n','<break time="1.5s"/>\n').replace('[low voice] ','').replace('...',' <break time="0.8s"/>')
    v2.append(f"=== CHUNK {n} (do not paste this line) ===\n{b}")
open('villisca_voiceover_ElevenV3_TEMP-phonetics.txt','w').write('\n\n'.join(v3)+'\n')
open('villisca_voiceover_MultilingualV2_TEMP-phonetics.txt','w').write('\n\n'.join(v2)+'\n')
for r in rows:
    print(r[0],'words',r[1],'lines',r[2],'start %d:%02d'%(r[3]//60,r[3]%60),'dur',r[4])
print('total words',tw,'runtime %d:%02d'%(t//60,t%60),'net wpm',round(tw/((t-20)/60),1))

import csv
S={"01":[("Q1","Text card: Stillinger testimony, 'My wife did, yes.'","Inquest"),("D9","Sanborn map: town, slow find of the block","Sanborn 1893"),("Q1","Text card: 'about three different times'","Inquest"),("M1","Floor plan, house only, blank","Diagram"),("M2","Empty inventory ledger, ruled lines","Diagram"),("D8","Day Book page, wide","DB"),("D8","Day Book headline crop","DB"),("M4","Year line 1912 to 1931, empty","Diagram")],
"02":[("M2","Ledger: first entry, 'The people'","Diagram"),("D8","Day Book: portrait crop, Joe Moore [VERIFY which face]","DB"),("D8","Day Book: portrait crop, Sarah Moore [VERIFY]","DB"),("D3","Bee: line about Herman's piece, highlighted","B27"),("D8","Day Book: child portrait crop [VERIFY identity]","DB"),("Q2","Text card: ages, both versions side by side","B27"),("Q3","Text card: Blanche Stillinger, 6 p.m. call","Inquest"),("D9","Map: church to house, three blocks","Sanborn 1893")],
"03":[("M1","Floor plan: doors marked locked","Diagram"),("Q4","Text card: Ross Moore, did not wait","Inquest"),("M1","Floor plan: room off the parlor lit","Diagram"),("Q5","Text card: Selley, house locked, keys with Peckham","Inquest"),("M2","Ledger: 'Keys: Mary Peckham'","Diagram"),("M1","Floor plan: stairs, south room","Diagram"),("BLK","Black, Williams quote as lower text","Inquest"),("BLK","Black, 5 s silence, no sound","None")],
"04":[("M2","Ledger: 'Ax', 'Bacon in flour sack'","B15"),("D5","Bee: exhibit list, wide","B15"),("D5","Bee: crop, flour sack line","B15"),("M2","Ledger: 'Lamp', 'Skirts and aprons'","Inquest"),("Q6","Text card: 'no finger marks', coroner 1917","IA"),("M1","Floor plan: every room, dots appear, no count","Diagram"),("Q7","Text card: Guard, 10:30 or noon","Diagram"),("Q8","Text card: Jessie Moore, family pictures","Inquest"),("M2","Ledger: lines struck through: bedding, furnishings","Epperly")],
"05":[("Q9","Text card: dateline Omaha, 15 June 1912","IA"),("M3","Evolution: 'closet, off the girls' room'","IA"),("M3","Evolution: add 'watch chain, in the bed'","IA"),("D5","Bee: 'closet in an upstairs room'","B15"),("M3","Evolution: 'cigarettes, heel print'","Epperly"),("M3","Evolution: 'suit boxes, not crushed'","Epperly"),("M3","Evolution: 'attic' added, marked 2020s","Diagram"),("D5","Bee: 'piece of key chain', 'watch'","B15"),("M3","Evolution: whole chain of changes","Diagram")],
"06":[("Q10","Text card: Council Bluffs, 21 Aug 1912","IA"),("M2","Ledger: 'Photograph, retina', stamped NOT FOUND","Diagram"),("M4","Year line: five marks in 1912","Diagram"),("Q11","Text card: five names, no conviction","IA"),("M2","Ledger: column 'Who pays', empty","Diagram")],
"07":[("M4","Year line: 1916","Diagram"),("D6","Bee: Wilkerson passage, wide","B1"),("D3","Bee: slander suit passage","B27"),("Q12","Text card: $60,000, lost","B27"),("M3","Sound to man: 'hooting', 1912","Inquest"),("M3","Sound to man: 'a woman moaning'","Inquest"),("M1","Floor plan: street, a few houses","Diagram"),("D3","Bee: Landers passage crop","B27"),("BLK","Black, 5 s silence","None"),("M3","Sound to man: 'Albert Jones', marked 'never charged'","B27")],
"08":[("D1","Bee 19 Sep: page, wide","B19a"),("Q13","Text card: charge, Lena Stillinger only","B27"),("D3","Bee: Kelly history passage","B27"),("D2","Bee: Sidney ticket record","B19b"),("D2","Bee: Lahman passage, handcuffs","B19b"),("D2","Bee: 'automobile thief' crop","B19b"),("D2","Bee: 'eighty-seven paragraphs' crop","B19b"),("D2","Bee: 'That's a lie' crop","B19b"),("D1","Confession: opening oath lines","B19a"),("D1","Confession: 'slay utterly' crop","B19a"),("D1","Confession: order of rooms crop","B19a"),("Q14","Counter card: 15, 25, 51","B27"),("D3","Bee: Havner's count, crop","B27"),("D1","Bee: 'no recollection' crop","B19a")],
"09":[("D4","Bee 29 Sep: committee passage","B29"),("Q1","Text card returns: 'about three different times'","Inquest"),("D3","Bee 27 Sep: 'Stillinger as president' crop","B27"),("BLK","Black, 5 s silence","None")],
"10":[("D4","Bee: 'Twenty ballots' crop","B29"),("D4","Bee: Brown, insanity instruction crop","B29"),("Q15","Text card: Nov 1917, not guilty","IA"),("M4","Year line: 1931","Diagram"),("Q16","Text card: Detroit, no clipping until 1 Jan 2027","IA"),("Q6","Text card returns: 'no finger marks'","IA"),("BLK","Black, 5 s silence, then count 6 of 8 on text","IA")],
"11":[("M2","Ledger: all carried-in items fade","Diagram"),("M2","Ledger: House, Ax, Photographs remain","Epperly"),("M4","Year line: full","Diagram"),("D8","Day Book: the eight faces, wide [VERIFY]","DB"),("Q1","Text card: 'about three different times'","Inquest"),("TXT","Disclaimer card, 8 s","None")]}
C={"Inquest":"Coroner's Inquest, 11 June 1912 [VERIFY vs facsimile]","DB":"The Day Book (Chicago), 14 June 1912","B27":"Omaha Daily Bee, 27 Sept 1917, p. 4","B19a":"Omaha Daily Bee, 19 Sept 1917, p. 1","B19b":"Omaha Daily Bee, 19 Sept 1917, p. 2","B15":"Omaha Daily Bee, 15 Sept 1917, p. 6","B29":"Omaha Daily Bee, 29 Sept 1917, p. 2","B1":"Omaha Daily Bee, 1 Sept 1917, p. 2","IA":"Newspaper report, as transcribed, IAGenWeb [find original]","Epperly":"Comment by E. Epperly, Iowa Cold Cases, 2026","Sanborn 1893":"Sanborn Map, Villisca, 1893, Library of Congress","Diagram":"Diagram by [channel]","None":""}
T=0;out=[];durs=dict((r[0],r[4]) for r in rows)
mv=["Hold","Push 1.00 to 1.10, ease in/out","Hold","Push 1.00 to 1.15, ease in/out"]
for n in sorted(S):
    L=S[n];d=durs[n]/len(L)
    assert 6<=d<=12,(n,d)
    for i,(c,desc,cit) in enumerate(L):
        out.append(("%d:%02d"%(T//60,T%60),c,desc,C[cit],round(d,1),"None" if c=="BLK" else mv[i%4]));T+=d
w=csv.writer(open('villisca_shot_list.csv','w',newline=''));w.writerow(["Timestamp","Image code","What shows","On-screen citation","Hold (s)","Movement"]);w.writerows(out)
print(len(out),'shots')
