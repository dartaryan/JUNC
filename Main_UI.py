from Main_Diagram import Diagram


ui_junc = Diagram()


ui_junc.SO.EVE.L = 40
print(ui_junc.SO.EVE.L)


ui_junc.SO.LAN.RL[0] = 1
ui_junc.SO.LAN.RL[1] = 0
print(ui_junc.SO.LAN.Organize_arrows_order())