from Core.conforming_ga.ga_g2 import extension_decision

def test_extension_only_after_base_and_only_over_one_percent_last_50():
 h=[1.0]*449+[1.0]+[1.02]*50
 assert extension_decision(h,500,500)==600
 h=[1.0]*450+[1.01]*50
 assert extension_decision(h,500,500)==500

def test_extension_is_in_100_generation_steps_and_caps_at_800():
 h=[1.0]*550+[1.02]*50
 assert extension_decision(h,600,600)==700
 h=[1.0]*650+[1.02]*50
 assert extension_decision(h,700,700)==800
 h=[1.0]*750+[1.02]*50
 assert extension_decision(h,800,800)==800
