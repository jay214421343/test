#!/usr/bin/env python3
"""ARVEEPrison v1.2.4 patch over the verified v1.2.3 sources.
Strict anchors: fail the GitHub build if our expected old code changed.
"""
from pathlib import Path
root = Path('src/main/java/world/arvee/prison')
def rewrite(path, old, new):
    p=Path(path)
    s=p.read_text(encoding='utf-8')
    assert old in s, 'Missing expected anchor in '+str(p)+': '+old[:90]
    p.write_text(s.replace(old,new,1),encoding='utf-8')
pricing = '''package world.arvee.prison;

/** Deterministic, overflow-safe token pricing. No Bukkit dependency. */
public final class PrisonEnchantPricing {
    private PrisonEnchantPricing() {}
    public static final long MAX_PRICE = Long.MAX_VALUE / 8L;
    public static long levelCost(long base,int nextLevel,double exponent,double multiplier){
        if(base<1L)base=1L;
        if(nextLevel<1)nextLevel=1;
        if(!Double.isFinite(exponent))exponent=1.25;
        if(!Double.isFinite(multiplier))multiplier=1.0;
        exponent=Math.max(0.2,Math.min(2.5,exponent));
        multiplier=Math.max(0.05,Math.min(3.0,multiplier));
        double result=((double)base)*multiplier*Math.pow(nextLevel,exponent);
        if(!Double.isFinite(result)||result>=MAX_PRICE)return MAX_PRICE;
        return Math.max(1L,(long)Math.ceil(result));
    }
}
'''
(root/'PrisonEnchantPricing.java').write_text(pricing)
old = '''    private long price(Player user,Perk p){
        int next=level(user.getUniqueId(),p)+1;
        double cost=plugin.getConfig().getDouble("abyss-enchants."+p.id+".base-cost",p.cost)*Math.pow(next,1.65);
        if(!Double.isFinite(cost)||cost>Long.MAX_VALUE/8)return Long.MAX_VALUE/8;
        return Math.max(1,(long)Math.ceil(cost));
    }
'''
new = '''    /** One authoritative price calculation for every menu and purchase path. */
    public long levelPrice(String name,int nextLevel){
        Perk perk=find(name);
        if(perk==null)return PrisonEnchantPricing.MAX_PRICE;
        String global="abyss-enchants.pricing.";
        String local="abyss-enchants."+perk.id+".";
        long base=Math.max(1L,plugin.getConfig().getLong(local+"base-cost",perk.cost));
        double exponent=plugin.getConfig().getDouble(local+"cost-exponent",
            plugin.getConfig().getDouble(global+"exponent",1.25));
        double multiplier=plugin.getConfig().getDouble(local+"cost-multiplier",
            plugin.getConfig().getDouble(global+"multiplier",1.0));
        return PrisonEnchantPricing.levelCost(base,nextLevel,exponent,multiplier);
    }
    private long price(Player user,Perk p){
        return levelPrice(p.id,level(user.getUniqueId(),p)+1);
    }
'''
rewrite(root/'PrisonEnchantEngine.java',old,new)
rewrite(root/'PrisonEnchantEngine.java','Math.min(p.max,modern+plugin.expansion().enchantLevel(id,p.id))','Math.min(max(p),modern+plugin.expansion().enchantLevel(id,p.id))')
rewrite(root/'PrisonEnchantEngine.java','Math.min(p.max,modern+plugin.profileByUuid(id).jackhammer)','Math.min(max(p),modern+plugin.profileByUuid(id).jackhammer)')
old = '''    private static long enchantCost(ArveePrison plugin, Enchant e, int nextLevel) {
        double raw = plugin.getConfig().getDouble("abyss-enchants." + e.id + ".base-cost", e.baseCost)
            * Math.pow(nextLevel, 1.65);
        if (!Double.isFinite(raw) || raw > Long.MAX_VALUE / 8) return Long.MAX_VALUE / 8;
        return Math.max(1, (long) Math.ceil(raw));
    }
'''
new = '''    private static long enchantCost(ArveePrison plugin, Enchant e, int nextLevel) {
        // GUI quote must agree with the exact server-side purchase price.
        return plugin.enchants().levelPrice(e.id, nextLevel);
    }
'''
rewrite(root/'PrisonUnifiedMenu.java',old,new)
rewrite(root/'PrisonUnifiedMenu.java','"&718 permanent abilities", "&7No additional pages"','"&718 permanent abilities", "&7Lower, configurable token prices", "&7No additional pages"')
rewrite('src/main/resources/config.yml',
'''abyss-enchants:
  token_luck:''',
'''abyss-enchants:
  # v1.2.4: reduced scaling. Token Luck 25 -> 26 ~5,872 tokens (was 21,613).
  # Even old, existing config.yml files use these new Java fallback defaults.
  pricing:
    exponent: 1.25
    multiplier: 1.0
  # Optional per-enchant: token_luck.cost-exponent / .cost-multiplier
  token_luck:''')
p=root/'ArveePrison.java'
s=p.read_text()
start=s.index('    public void upgrade(Player player, String type) {')
end=s.index('    private boolean admin(',start)
s=s[:start]+'''    public void upgrade(Player player, String type) {
        // One validated path for single, +10 and bulk purchases.
        if(!"autosell".equals(type)){upgradeBulk(player,type,1);return;}
        PrisonProfile p=profile(player);
        if(autosellEntitled(player,p)){
            message(player,"&eAuto-Sell already available. Toggle with /autosell.");return;
        }
        long cost=Math.max(1L,getConfig().getLong("pickaxe.autosell-token-cost",500));
        if(p.tokens<cost){message(player,"&cAuto-Sell costs &e"+Amounts.format(cost)+" &ctokens.");return;}
        p.tokens-=cost;
        p.autoSellUnlocked=true;
        p.autoSellEnabled=true;
        message(player,"&aAuto-Sell unlocked and enabled!");
        grantPickaxe(player);
        if(!enchants.refresh(player))menus.openUpgrades(player);
    }

'''+s[end:]
p.write_text(s)
rewrite(root/'ArveePrison.java',
'''            case "saveall" -> {
                profiles.save();gangs.save();seasons.save();miningEvents.save();expansion.save();industry.save();plots.save();foundry.save();prestigeCodex.save();endgameMarket.save();tutorial.save();ascension.save();database.queueDocuments();
                message(sender,"&aSaved all player, gang and season ledgers. SQL snapshot queued.");
            }''',
'''            case "saveall" -> {
                profiles.save();gangs.save();seasons.save();miningEvents.save();
                expansion.save();industry.save();plots.save();
                foundry.save();prestigeCodex.save();endgameMarket.save();tutorial.save();
                ascension.save();prestigeAscension.save();enchants.save();
                artifacts.save();territory.save();industryModules.save();
                progression.save();lifestyle.save();storage.flush();
                boostItems.save();notifications.save();pickaxeMastery.save();
                mineExplosives.save();treats.save();petTrading.save();
                database.queueDocuments();
                message(sender,"&aSaved player ledgers, Prestige Ascension, enchants, storage, boosts and progression. SQL snapshot queued.");
            }''')
rewrite(root/'ArveePrison.java','ARVEE Prison v1.2.1 Mining & Storage enabled.','ARVEE Prison v1.2.4 QoL & Token Balance enabled.')
rewrite('build.gradle.kts','version = "1.2.3"','version = "1.2.4"')
rewrite('src/main/resources/plugin.yml','version: 1.2.3','version: 1.2.4')
rewrite('tests/prestige_ascension_regression.py',"assert 'version: 1.2.3' in yml","assert 'version: 1.2.4' in yml")
print('Patched v1.2.4: shared economics, consistent upgrade flow, manual save completeness')
