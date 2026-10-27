from pathlib import Path
root=Path("src/main/java/world/arvee/prison")
def change(filename,old,new):
    path=root/filename
    txt=path.read_text(encoding="utf-8")
    assert old in txt,(filename,old[:80])
    path.write_text(txt.replace(old,new),encoding="utf-8")
p=root/"PrisonBoostItems.java"
s=p.read_text(encoding="utf-8")
start=s.index("    /** Convert exact, unexpired active time back into a voucher.")
stop=s.index("    public void command(Player p,String[] args){",start)
p.write_text(s[:start]+s[stop:],encoding="utf-8")
change("PrisonBoostItems.java",'''            case "withdraw"->{if(args.length<3){plugin.message(p,"&e/prisonbooster withdraw <money|tokens|fortune|server> <minutes>");return;}
                try{withdraw(p,args[1].toLowerCase(Locale.ROOT),Integer.parseInt(args[2]));}catch(NumberFormatException e){plugin.message(p,"&cMinutes must be a whole number.");}}''','''            case "withdraw"->plugin.message(p,"&cActivated boosts are non-refundable and cannot be withdrawn. &7Only unused vouchers can be merged or split.");''')
change("PrisonBoosterMenu.java",'"&7Withdraw personal active time into tradeable items"','"&cActivated boost time cannot be withdrawn"')
change("PrisonBoosterMenu.java",'''"&eRight-click: Withdraw 10 min active time",
                "&eShift-left: Withdraw 60 min active time"''','''"&cActive time is non-refundable",
                "&7Unused vouchers can still be merged or split"''')
change("PrisonBoosterMenu.java",'''            if(e.isRightClick()||e.isShiftClick())plugin.boostItems().withdraw(p,TYPES[i],e.isShiftClick()&&!e.isRightClick()?60:10);
            else plugin.boostItems().merge(p,TYPES[i]);open(p);return;''','''            if(e.isRightClick()||e.isShiftClick()){
                plugin.message(p,"&cActivated boosts cannot be withdrawn. &7Left-click to merge unused vouchers.");return;
            }
            plugin.boostItems().merge(p,TYPES[i]);open(p);return;''')
change("PrisonMenus.java",'"&7Manage, merge, split and withdraw boosters"','"&7Merge and split unused booster vouchers"')
change("ArveePrison.java",'List.of("buy","claim","merge","split","withdraw","menu","types","status")','List.of("buy","claim","merge","split","menu","types","status")')
p=Path("src/main/resources/plugin.yml")
s=p.read_text(encoding="utf-8")
old='''  arveeprison.booster.withdraw-server:
    description: Permit withdrawing shared global server booster time
    default: op
'''
assert old in s
p.write_text(s.replace(old,"").replace("version: 1.2.4","version: 1.2.5"),encoding="utf-8")
p=Path("build.gradle.kts")
s=p.read_text(encoding="utf-8")
assert 'version = "1.2.4"' in s
p.write_text(s.replace('version = "1.2.4"','version = "1.2.5"'),encoding="utf-8")
print("v1.2.5: all activated-boost withdrawal paths removed")