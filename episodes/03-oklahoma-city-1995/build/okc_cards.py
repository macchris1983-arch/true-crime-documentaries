import sys, json, os
sys.path.insert(0, "/home/claude/vid")
from draw import *

OUT = "/home/claude/okc/build/cards"; os.makedirs(OUT, exist_ok=True)
FBI = "FBI · public domain"
FBIH = "FBI history, Oklahoma City bombing case"
TRIAL = "Trial record, U.S. v. McVeigh and U.S. v. Nichols"
DOJ = "U.S. Justice Department statements, June 1995 and January 1997"
NG = "Oklahoma National Guard video, April 1995 · DVIDS · public domain"
IMP = "Defense Visual Information video, 1995 · DVIDS · public domain"
FEMA = "FEMA News Photo, April 26, 1995 · public domain"
DOD = "U.S. Air Force photo, SSgt Preston Chasteen, 1995 · public domain"
HS = "Carol M. Highsmith, Library of Congress · public domain"
FBIP = "FBI photo · public domain"
MIL = "U.S. military video, April 1995 · DVIDS · public domain"


def title():
    i, d = base()
    for t, F, y, col in [("THE MAN WHO WAS", f(SB, 170), 470, INK), ("ALREADY IN JAIL", f(SB, 170), 690, INK),
                         ("Oklahoma City · April 19, 1995", f(SER, 74), 960, HI)]:
        d.text(((W - d.textlength(t, font=F)) / 2, y), t, font=F, fill=col)
    return i


def welcome():
    i, d = base()
    for t, F, y, col in [("Welcome to story timez.", f(SER, 104), 430, INK), ("True crime told from the record.", f(SER, 70), 600, DIM),
                         ("If that's your kind of story, like, comment, and subscribe.", f(SER, 70), 720, DIM)]:
        d.text(((W - d.textlength(t, font=F)) / 2, y), t, font=F, fill=col)
    F = f(SB, 64); t = "SUBSCRIBE"; w = d.textlength(t, font=F) + 160; x0 = (W - w) / 2
    d.rounded_rectangle([x0, 930, x0 + w, 1060], radius=65, fill=(178, 34, 34)); d.text((x0 + 80, 958), t, font=F, fill=(255, 255, 255))
    F = f(MO, 46); t = "Link in the description"; d.text(((W - d.textlength(t, font=F)) / 2, 1130), t, font=F, fill=DIM)
    return i


def endcard():
    i, d = base()
    L = [("Sources are in the description.", f(SER, 70), 470, INK),
         ("168 people were killed, 19 of them children.", f(SER, 62), 600, DIM),
         ("Three men were convicted. The Army private in the second sketch was cleared.", f(SER, 56), 700, DIM),
         ("If this was worth your time: like, comment, and subscribe to story timez.", f(SER, 62), 900, HI)]
    for t, F, y, col in L:
        d.text(((W - d.textlength(t, font=F)) / 2, y), t, font=F, fill=col)
    return i


C = lambda big, kick="", attr="", size=118: (lambda: card(big, kick, attr, size))
# shot spec: (key, cue, kind, ref, cite)  kind: card | img | vid | blk
S = {
 "00a": [("c_1020", "At twenty past ten", "card", C("10:20 a.m. · Interstate 35", "OKLAHOMA · WEDNESDAY, APRIL 19, 1995"), TRIAL),
         ("c_pistol", "He found a pistol", "card", C("A pistol under the jacket."), TRIAL),
         ("c_jail", "He booked the driver", "card", C("Noble County Jail, Perry, Oklahoma."), TRIAL),
         ("v_fbi", "For the next two days", "vid", ("imp", 470), IMP),
         ("b_cell", "He was already in a cell", "blk", lambda: blk("He was already in a cell."), ""),
         ("i_jd2", "And the second man", "img", "jd2.png", FBI)],
 "00b": [("c_title", "@0", "card", title, "")],
 "00c": [("i_bldg", "This is the Oklahoma City", "img", "fema1562.jpg", FEMA),
         ("i_chairs", "A hundred and sixty-eight", "img", "mem61.jpg", HS),
         ("c_jury", "This is not a mystery", "card", C("A jury decided who did it."), ""),
         ("i_jd1", "It is a story about how", "img", "jd1_sketch.png", FBI),
         ("v_raw", "I'm going to show you the record", "vid", ("raw", 120), NG),
         ("c_welcome", "Welcome to story", "card", welcome, "")],
 "01": [("c_902", "At two minutes past nine", "card", C("9:02 a.m.", "THE ALFRED P. MURRAH FEDERAL BUILDING"), FBIH),
        ("i_night", "About a third of the building", "img", "fema1547.jpg", FEMA),
        ("i_cars", "More than three hundred", "img", "dod_cars.jpg", DOD),
        ("c_168", "The FBI counts", "card", C("168 killed.\nNineteen of them children.", "THE FBI'S COUNT"), FBIH),
        ("v_rain", "Several hundred more", "vid", ("raw", 30), NG),
        ("v_rubble", "It shows the search", "vid", ("raw", 400), NG),
        ("b_choice", "I will not show you", "blk", lambda: blk(), "")],
 "02": [("v_site", "On April twentieth", "vid", ("imp", 482), IMP),
        ("c_vin", "It carried a vehicle", "card", C("Axle → VIN → Ryder truck → a body shop in Junction City, Kansas", "THE TRACE", size=96), FBIH),
        ("l_kling", "The truck had been reserved", "card", lambda: ledger([("Name given", "ROBERT KLING"), ("Deposit", "APRIL 15"), ("Picked up", "APRIL 17")], "THE RENTAL"), TRIAL),
        ("i_jd1b", "The people at the body shop", "img", "jd1_sketch.png", FBI),
        ("i_jd2b", "And John Doe Number Two", "img", "jd2.png", FBI)],
 "03": [("c_back", "Go back to the nineteenth", "card", C("April 19 · about 10:20 a.m.", "INTERSTATE 35, NORTH OF OKLAHOMA CITY"), TRIAL),
        ("c_tag", "Trooper Charles Hanger", "card", C("No tag on the back.", "TROOPER CHARLES HANGER"), TRIAL),
        ("c_mile", "He pulled it over", "card", C("Between mile markers 202 and 203."), TRIAL),
        ("i_photo", "The driver handed him", "img", "jd1.jpg", FBI),
        ("c_gun", "When the trooper reached", "card", C("“I have a gun.”", "", "Trooper Hanger's trial testimony, November 1997"), TRIAL),
        ("c_none", "The dispatcher found", "card", C("No warrants. No record."), TRIAL),
        ("l_chg", "The trooper booked him", "card", lambda: ledger(["Transporting a loaded firearm", "Carrying a weapon unlawfully", "No license plate", "No proof of insurance"], "MISDEMEANOR CHARGES"), TRIAL),
        ("b_know", "He did not know", "blk", lambda: blk(), "")],
 "04": [("i_jd1c", "On April twenty-first", "img", "jd1_sketch.png", FBI),
        ("e_two", "How the name came back", "card", lambda: evo([("FBI history", "Motel employees gave the name"), ("Trial chronology", "A former co-worker knew the face")], "HOW THE NAME CAME BACK"), FBIH),
        ("c_rec", "Either way, agents ran", "card", C("FBI national records check.", "APRIL 21, 1995"), FBIH),
        ("c_cust", "Timothy McVeigh was in custody", "card", C("In custody in Perry, Oklahoma.\nSince the morning of the bombing."), FBIH),
        ("c_agents", "Federal agents reached him", "card", C("Federal agents get there first.", "PERRY, OKLAHOMA · APRIL 21"), FBIH),
        ("c_nich", "The same day, in Herington", "card", C("Terry Nichols turns himself in.", "HERINGTON, KANSAS · APRIL 21"), TRIAL),
        ("b_04", "@end", "blk", lambda: blk(), "")],
 "05": [("i_jd2c", "That left the second sketch", "img", "jd2.png", FBI),
        ("c_tips", "Tips poured in", "card", C("At least a dozen men picked up."), ""),
        ("c_june", "Then, in June", "card", C("June 1995.\nThe Justice Department says it found him.", size=104), DOJ),
        ("c_pvt", "He was an Army private", "card", C("An Army private, renting a truck of his own.", size=104), DOJ),
        ("e_day", "A day apart", "card", lambda: evo([("April 17", "The first man picks up his truck"), ("A day apart", "The private comes in with another soldier")], "THE SAME BODY SHOP"), DOJ),
        ("c_clr", "The private had nothing", "card", C("He had nothing to do with the bombing."), DOJ),
        ("c_gj", "A county grand jury", "card", C("Eighteen months. The same conclusion.", "OKLAHOMA COUNTY GRAND JURY"), ""),
        ("i_jd2d", "But the sketch had already", "img", "jd2.png", FBI),
        ("b_sold", "The record says he was", "blk", lambda: blk("A soldier renting a truck."), "")],
 "06": [("c_den", "The trial was moved", "card", C("Denver, 1997.", "CHANGE OF VENUE"), TRIAL),
        ("l_mcv", "On June second", "card", lambda: ledger([("All eleven counts", "GUILTY"), ("June 13, 1997", "DEATH")], "TIMOTHY McVEIGH"), TRIAL),
        ("l_nic", "Terry Nichols was tried", "card", lambda: ledger([("Conspiracy", "GUILTY"), ("Involuntary manslaughter", "GUILTY"), ("Using a weapon of mass destruction", "ACQUITTED"), ("Sentence", "LIFE")], "TERRY NICHOLS · FEDERAL TRIAL"), TRIAL),
        ("c_2004", "In two thousand four", "card", C("2004: more than 160 murder convictions.\nNo death sentence.", "OKLAHOMA STATE TRIAL", size=100), TRIAL),
        ("c_fort", "Michael Fortier", "card", C("Knew. Warned no one. Testified.\nTwelve years.", "MICHAEL FORTIER"), TRIAL)],
 "07": [("c_may", "The case had one more turn", "card", C("May 2001."), ""),
        ("c_pages", "In May, two thousand one", "card", C("More than 4,000 pages never given to the defense.", "THE JUSTICE DEPARTMENT", size=100), TRIAL),
        ("c_june11", "On June eleventh", "card", C("June 11, 2001."), TRIAL),
        ("b_07", "@end", "blk", lambda: blk(), "")],
 "08": [("v_bldg", "So here is what the record holds", "vid", ("imp", 120), IMP),
        ("v_face", "A truck. An axle", "vid", ("b19", 572), MIL),
        ("c_plate", "A trooper who stopped", "card", C("A car with no plate."), ""),
        ("i_jd2e", "And here is what was added", "img", "jd2.png", FBI),
        ("l_conv", "The courts convicted three men", "card", lambda: ledger([("Timothy McVeigh", "EXECUTED 2001"), ("Terry Nichols", "LIFE"), ("Michael Fortier", "12 YEARS"), ("The Army private", "CLEARED")], "THE RECORD"), TRIAL),
        ("i_mem", "Where the memorial now stands", "img", "mem62.jpg", HS),
        ("c_disc", "This film is drawn from", "card", C("Drawn from federal records, court filings and the reporting of the time. A report is not proof.", size=80), ""),
        ("i_mem2", "And the arrest that held him", "img", "mem804.jpg", HS)],
 "09": [("c_end", "@0", "card", endcard, "")],
}
plan = {}
for ch, shots in S.items():
    plan[ch] = []
    for key, cue, kind, ref, cite in shots:
        if kind in ("card", "blk"):
            ref().convert("RGB").resize((1920, 1080), Image.LANCZOS).save(f"{OUT}/{key}.png")
            plan[ch].append({"key": key, "cue": cue, "kind": "card", "src": f"cards/{key}.png", "cite": cite, "black": kind == "blk"})
        elif kind == "img":
            plan[ch].append({"key": key, "cue": cue, "kind": "img", "src": ref, "cite": cite})
        else:
            plan[ch].append({"key": key, "cue": cue, "kind": "vid", "src": ref[0], "t": ref[1], "cite": cite})
json.dump(plan, open("/home/claude/okc/build/plan.json", "w"), indent=1)
print(sum(len(v) for v in plan.values()), "shots")
