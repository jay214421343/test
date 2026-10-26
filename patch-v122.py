from pathlib import Path
root=Path('src/main/java/world/arvee/prison')
p=root/'PrisonMineExplosives.java'
s=p.read_text()
assert s.count('@EventHandler public void use(PlayerInteractEvent e){')==1
s=s[:s.index('    @EventHandler public void use(PlayerInteractEvent e){')]
s=s.replace('import org.bukkit.event.EventHandler;', 'import org.bukkit.event.EventHandler;\nimport org.bukkit.event.EventPriority;')
s+="\n    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=false)\n    public void use(PlayerInteractEvent e){\n        if(e.getHand()!=EquipmentSlot.HAND)return;\n        Player p=e.getPlayer();\n        String type=kind(p.getInventory().getItemInMainHand());\n        if(type==null)return;\n        Action action=e.getAction();\n        if(action!=Action.RIGHT_CLICK_BLOCK&&action!=Action.RIGHT_CLICK_AIR)return;\n        e.setCancelled(true);\n        if(!plugin.getConfig().getBoolean(\"mine-explosives.enabled\",true)){\n            plugin.message(p,\"&cMine explosives are currently disabled.\");return;\n        }\n        if(blasting.contains(p.getUniqueId())){\n            plugin.message(p,\"&cPrevious blast is still mining. No item consumed.\");return;\n        }\n        Block origin=action==Action.RIGHT_CLICK_BLOCK?e.getClickedBlock():p.getTargetBlockExact(8);\n        if(origin==null){plugin.message(p,\"&cAim at an ore block in a Prison mine.\");return;}\n        final int rank=plugin.worlds().rankFor(origin.getWorld());\n        final boolean prestige=plugin.prestigeMines().isPrestigeWorld(origin.getWorld());\n        if(!prestige&&rank<0){\n            plugin.message(p,\"&cBombs only work in public or prestige Prison mines.\");return;\n        }\n        if(prestige){\n            if(plugin.profile(p).prestige<plugin.prestigeMines().requiredPrestige(origin.getWorld())){\n                plugin.message(p,\"&cYou haven't unlocked this prestige mine.\");return;\n            }\n            if(plugin.prestigeMines().isResetting(origin.getWorld())){\n                plugin.message(p,\"&cPrestige mine is resetting. No bomb consumed.\");return;\n            }\n        }else if(plugin.worlds().isResetting(rank)||!plugin.canEnterMine(p,rank)){\n            plugin.message(p,\"&cMine is locked or resetting. No bomb consumed.\");return;\n        }\n        int cap=Math.max(1,Math.min(2000,plugin.getConfig().getInt(\n            \"mine-explosives.\"+(type.equals(\"nuke\")?\"nuke\":\"bomb\")+\"-limit\",type.equals(\"nuke\")?850:120)));\n        int radius=type.equals(\"nuke\")?11:5;\n        int height=type.equals(\"nuke\")?10:4;\n        List<Block> candidates=new ArrayList<>();\n        if(eligible(origin,prestige,rank))candidates.add(origin);\n        for(int dy=-height;dy<=height;dy++)for(int dx=-radius;dx<=radius;dx++)for(int dz=-radius;dz<=radius;dz++){\n            if(dx==0&&dy==0&&dz==0)continue;\n            if(dx*dx+dz*dz+dy*dy>radius*radius)continue;\n            Block b=origin.getRelative(dx,dy,dz);\n            if(!b.getWorld().isChunkLoaded(b.getX()>>4,b.getZ()>>4))continue;\n            if(eligible(b,prestige,rank))candidates.add(b);\n        }\n        if(candidates.isEmpty()){\n            plugin.message(p,\"&cNo mineable ore in range. Nothing consumed.\");return;\n        }\n        boolean directSell=plugin.getConfig().getBoolean(\"mine-explosives.instant-sell\",true);\n        int first=-1;\n        for(int i=0;i<candidates.size();i++){\n            if(directSell||plugin.backpackHasRoom(p,plugin.profile(p),prestige?25:rank,candidates.get(i).getType())){\n                first=i;break;\n            }\n        }\n        if(first<0){\n            plugin.message(p,\"&cBackpack full: /sell or enable Auto-Sell. No explosive consumed.\");return;\n        }\n        if(first!=0){Block start=candidates.remove(first);candidates.add(0,start);}\n        // Mine one block synchronously BEFORE consuming the voucher. A no-op\n        // blast can never destroy an item.\n        if(!mineOne(p,candidates.get(0),prestige,rank,directSell)){\n            plugin.message(p,\"&cCannot mine that ore. Explosive was not consumed.\");return;\n        }\n        ItemStack held=p.getInventory().getItemInMainHand();\n        if(type.equals(kind(held))){\n            if(held.getAmount()==1)p.getInventory().setItemInMainHand(null);\n            else{held.setAmount(held.getAmount()-1);p.getInventory().setItemInMainHand(held);}\n        }else plugin.getLogger().warning(\"Explosive item changed during mining for \"+p.getName());\n        blasting.add(p.getUniqueId());\n        origin.getWorld().playSound(origin.getLocation(),Sound.ENTITY_GENERIC_EXPLODE,.65f,type.equals(\"nuke\")?.7f:1.1f);\n        origin.getWorld().spawnParticle(Particle.EXPLOSION,origin.getLocation().add(.5,.5,.5),3);\n        plugin.message(p,\"&6&l\"+(type.equals(\"nuke\")?\"MINE NUKE\":\"MINE BOMB\")+\n            \" &7» &eDetonated! Mining up to \"+cap+\" blocks...\");\n        if(cap==1||candidates.size()==1){\n            blasting.remove(p.getUniqueId());plugin.message(p,\"&aBlast complete: 1 block mined.\");return;\n        }\n        new BukkitRunnable(){\n            int index=1,broken=1;\n            @Override public void run(){\n                if(!plugin.isEnabled()||!p.isOnline()||p.getWorld()!=origin.getWorld()){\n                    blasting.remove(p.getUniqueId());cancel();return;\n                }\n                if(prestige?plugin.prestigeMines().isResetting(origin.getWorld()):plugin.worlds().isResetting(rank)){\n                    finish(\"&eMine reset interrupted the blast.\");return;\n                }\n                int batch=Math.max(1,Math.min(100,plugin.getConfig().getInt(\"mine-explosives.per-tick-blocks\",60)));\n                int scanned=0,mined=0;\n                while(index<candidates.size()&&broken<cap&&mined<batch&&scanned<batch*20){\n                    Block block=candidates.get(index++);scanned++;\n                    if(!eligible(block,prestige,rank))continue;\n                    if(!directSell&&!plugin.backpackHasRoom(p,plugin.profile(p),prestige?25:rank,block.getType())){\n                        finish(\"&eBackpack filled during blast. Use /sell.\");return;\n                    }\n                    if(mineOne(p,block,prestige,rank,directSell)){broken++;mined++;}\n                }\n                if(index>=candidates.size()||broken>=cap)finish(null);\n            }\n            private void finish(String reason){\n                blasting.remove(p.getUniqueId());cancel();\n                plugin.message(p,\"&6&l\"+(type.equals(\"nuke\")?\"MINE NUKE\":\"MINE BOMB\")+\" &7» &a\"+broken+\" blocks mined!\");\n                if(reason!=null)plugin.message(p,reason);\n            }\n        }.runTaskTimer(plugin,1L,1L);\n    }\n    private boolean eligible(Block b,boolean prestige,int rank){\n        if(b.getType().isAir()||b.getType()==Material.BEDROCK)return false;\n        return prestige?plugin.prestigeMines().isMineBlock(b)\n            :rank>=0&&!plugin.worlds().isResetting(rank)&&plugin.worlds().isMineBlock(b);\n    }\n    private boolean mineOne(Player p,Block b,boolean prestige,int rank,boolean directSell){\n        if(!eligible(b,prestige,rank))return false;\n        if(prestige)return plugin.prestigeMines().bonusBreak(p,b,directSell);\n        if(!plugin.canEnterMine(p,rank))return false;\n        Material m=b.getType();\n        b.setType(Material.AIR,false);\n        plugin.creditBlock(plugin.profile(p),rank,m,true,1.0,directSell);\n        plugin.worlds().recordBreak(rank);\n        return true;\n    }\n}\n"
p.write_text(s)

p=root/'ArveePrison.java'
s=p.read_text()
old='''    void creditBlock(PrisonProfile p, int rank, Material blockType, boolean customPickaxe,double regionMultiplier) {
        Player miner = Bukkit.getPlayer(p.uuid);
        boolean selling = miner != null ? autosellActive(miner, p) : p.autoSellUnlocked && p.autoSellEnabled;'''
assert s.count(old)==1
new='''    void creditBlock(PrisonProfile p, int rank, Material blockType, boolean customPickaxe,double regionMultiplier) {
        creditBlock(p,rank,blockType,customPickaxe,regionMultiplier,false);
    }
    /** Voucher-mined ore can safely use instant-sale without changing AutoSell settings. */
    void creditBlock(PrisonProfile p, int rank, Material blockType, boolean customPickaxe,double regionMultiplier,boolean forceSell) {
        Player miner = Bukkit.getPlayer(p.uuid);
        boolean selling = forceSell || (miner != null ? autosellActive(miner, p) : p.autoSellUnlocked && p.autoSellEnabled);'''
p.write_text(s.replace(old,new))

p=root/'PrisonPrestigeMines.java'
s=p.read_text()
old='''    boolean bonusBreak(Player p,Block block){Zone z=zone(block.getWorld());if(z==null||!isMineBlock(block)||plugin.profile(p).prestige<z.requirement)return false;
        State state=states.get(z);Material type=block.getType();PrisonProfile profile=plugin.profile(p);
        if(!plugin.backpackHasRoom(p,profile,25,type))return false;
        block.setType(Material.AIR,false);
        state.minedCount=Math.min(totalBlocks(state.world),state.minedCount+1);
        plugin.creditBlock(profile,25,type,true,incomeMultiplier(state.world));return true;
    }'''
assert s.count(old)==1
new='''    boolean bonusBreak(Player p,Block block){return bonusBreak(p,block,false);}
    boolean bonusBreak(Player p,Block block,boolean directSale){
        Zone z=zone(block.getWorld());if(z==null||!isMineBlock(block)||plugin.profile(p).prestige<z.requirement)return false;
        State state=states.get(z);Material type=block.getType();PrisonProfile profile=plugin.profile(p);
        if(!directSale&&!plugin.backpackHasRoom(p,profile,25,type))return false;
        block.setType(Material.AIR,false);
        state.minedCount=Math.min(totalBlocks(state.world),state.minedCount+1);
        plugin.creditBlock(profile,25,type,true,incomeMultiplier(state.world),directSale);return true;
    }'''
p.write_text(s.replace(old,new))
p=Path('src/main/resources/config.yml')
s=p.read_text()
assert 'mine-explosives:\n  enabled: true' in s
s=s.replace('mine-explosives:\n  enabled: true',
'''mine-explosives:
  enabled: true
  # Explosive-mined ore instantly sells, even with a full backpack.
  # Turn off to require ordinary backpack space.
  instant-sell: true''')
p.write_text(s)
for path in [Path('build.gradle.kts'),Path('src/main/resources/plugin.yml')]:
    s=path.read_text()
    assert '1.2.1' in s
    path.write_text(s.replace('1.2.1','1.2.2'))
print('v1.2.2 data-compatible hotfix applied')
