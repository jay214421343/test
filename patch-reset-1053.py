from pathlib import Path

java=Path("src/main/java/world/arvee/prison/PrisonPrestigeMines.java")
s=java.read_text(encoding="utf-8")
needle="private static final int GEOMETRY_VERSION=2;"
assert s.count(needle)==1
s=s.replace(needle, needle+"\n    // Preserve original 20-minute reset cadence regardless of mine size.\n    private static final int RESET_MINUTES=20;")
old='    private int resetMinutes(){return Math.max(2,plugin.getConfig().getInt("prestige-mines.reset-minutes",12));}\n'
assert s.count(old)==1
s=s.replace(old, "")
assert s.count("resetMinutes()")==2
s=s.replace("resetMinutes()", "RESET_MINUTES")
old_condition="""            if(s.refillIndex<0 && (System.currentTimeMillis()-s.lastReset>=RESET_MINUTES*60*1000L
                || s.minedCount>=totalBlocks(s.world)*.80))s.refillIndex=0;"""
assert s.count(old_condition)==1
s=s.replace(old_condition, "            if(s.refillIndex<0 && System.currentTimeMillis()-s.lastReset>=RESET_MINUTES*60*1000L)s.refillIndex=0;")
assert "minedCount>=totalBlocks" not in s
java.write_text(s,encoding="utf-8")

conf=Path("src/main/resources/config.yml")
c=conf.read_text(encoding="utf-8")
old_config="  reset-minutes: 12 # faster than 20min A-Z schedule; also resets at 20% remaining\n"
assert c.count(old_config)==1
c=c.replace(old_config, "  # Prestige worlds use their original 20-minute schedule, with no early depletion reset.\n  # Legacy v1.0.5.2 prestige reset-minutes configs are ignored.\n")
conf.write_text(c,encoding="utf-8")

for f in [Path("src/main/resources/plugin.yml"),Path("build.gradle.kts")]:
    t=f.read_text(encoding="utf-8")
    assert "1.0.5.2" in t
    f.write_text(t.replace("1.0.5.2", "1.0.5.3"),encoding="utf-8")
print("Verified: prestige-only 20-minute interval, no 80-percent trigger, Java 25 plugin v1.0.5.3")
