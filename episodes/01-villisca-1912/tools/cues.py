from shots import *
acc=["A closet, off the girls' room","Bags of cotton batting","The marks of a man","A piece of watch chain, in the bed"]
from draw import center,f,SER,DIM
def phone():
    i=card("“She phoned "+QT+".”","JOSEPH STILLINGER")
    import PIL.ImageDraw as ID;d=ID.Draw(i)
    center(d,["The summary records the coroner asking about “Sunday morning.”","The girls stayed Sunday night. He said she expected them back before school.","We read it as Monday, June 10. The sources do not agree."],f(SER,54),1080,DIM,78)
    return i
N={"phone":(phone,I),
"ages":((lambda:card("Lena: 11 or 12.\nIna: 8 or 9, or 6.","THE RECORDS DISAGREE")),"Coroner's inquest and trial reports, 1912 and 1917"),
"stay":((lambda:card("Blanche Stillinger thought that would be all right.","HER ACCOUNT")),I),
"locked":((lambda:plan(note="Locked. The key, next door.")),D),
"acc1":((lambda:ledger(acc[:1],"RETTA JOHNSON'S ACCOUNT")),IA),
"acc2":((lambda:ledger(acc[:3],"RETTA JOHNSON'S ACCOUNT")),IA),
"acc4":((lambda:ledger(acc,"RETTA JOHNSON'S ACCOUNT")),IA),
"chain1":((lambda:evo(c[:1],"THE CHAIN")),IA),
"retina":((lambda:ledger([("Photograph, from a retina","?")])),IA),
"five3":((lambda:card("A brother-in-law.\nA man with stained shoes.\nA farmhand who wrote about a vision.",size=86)),IA),
"comm":((lambda:card("The committee wanted the guilty man brought to justice.","ITS STATED AIM")),B29),
"named":((lambda:card("A man.\nHis wife.\nFour children.","THE DETROIT CONFESSION",size=100)),IA),
"form":((lambda:ledger([("Name","?")],"THE FORM")),D),
"three":((lambda:card("A stranger.\nA senator.\nA preacher who heard voices.")),""),
}
CUE={
"01":[(1,"On the morning"),(0,"My wife did"),("phone","She tried, he said"),(3,"That house was locked"),(5,"A crowd walked"),(7,"But here is what"),(6,"A closet."),(4,"I can't tell you")],
"02":[(1,"The first entry"),(2,"Sarah Moore was"),(3,"Herman was eleven"),(5,"Lena Stillinger took"),("ages","The records disagree"),(6,"At six o'clock"),("stay","Could they stay"),(7,"The pastor testified")],
"03":[(0,"Monday morning"),(2,"Joe's brother Ross"),(1,"He told the coroner"),(3,"And then he did"),(4,"and left the keys"),("locked","It is the last moment"),(5,"Dr. Williams climbed"),(6,"Dr. Williams told"),(7,"I lifted that off")],
"04":[(0,"So here is the first"),(1,"A piece of bacon"),(3,"A lamp on the floor"),(4,"Dr. Williams found"),(6,"Then the house was opened"),(5,"How many people"),(7,"What the record does"),(8,"Bedding was burned")],
"05":[(0,"Item one arrives"),("acc1","There is a closet"),("acc2","Bags of cotton"),("acc4","And in the girls' bed"),(3,"By the trial, five"),(4,"traces a version"),(5,"It says an undertaker"),(6,"Today, you will hear"),("chain1","A watch chain, in a bed"),(8,"By the trial,")],
"06":[(0,"August, nineteen twelve"),("retina","They got it"),(1,"I have found no such"),(2,"By the end of that year"),("five3","A brother-in-law"),(3,"A Sioux City porter"),(4,"The question had stopped")],
"07":[(0,"In nineteen sixteen"),(1,"Wilkerson's man"),(3,"He sued Wilkerson"),(6,"You have met Landers"),(4,"At the inquest"),(5,"The next day"),(7,"Four years later"),(8,"Albert Jones was never"),(9,"A sound")],
"08":[(0,"In nineteen seventeen"),(1,"He was charged with the murder"),(2,"He caught the five"),(3,"A station ticket"),(5,"A newspaper editor"),(7,"Kelly said,"),(8,"Its first lines"),(9,"In it, a voice"),(10,"He kills the children"),(12,"The attorney general"),(11,"Twenty-five times"),(13,"At trial, Kelly said")],
"09":[(0,"There is one more name"),(1,"Remember the man"),(2,"And Joseph Stillinger"),(3,"@END")],
"10":[("comm","The paper does not"),(0,"It did not believe"),(1,"One man, W. C. Brown"),(2,"In November"),(4,"A man in a Detroit"),(5,"Remember the coroner"),("named","He says he killed"),(6,"Six people")],
"11":[(1,"So here is the inventory"),(0,"Everything else was carried"),(2,"Much of it"),("form","That is what this kind"),("three","And a town will"),(3,"No one has ever"),(4,"The one thing in this file"),(5,"This film is drawn")]}
