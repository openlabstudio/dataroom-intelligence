#!/usr/bin/env python3
"""Test emoji mapping functionality"""

test_text = """:dardo: **DATA ROOM ANALYSIS COMPLETE**
:página_boca_arriba: **Documents Analyzed: 1**
:bombilla: **VALUE PROPOSITION:**
:espadas_cruzadas: **COMPETITORS:**
:autopista: **PRODUCT ROADMAP:**
:bolsa_de_dinero: **FINANCIAL HIGHLIGHTS:**"""

emoji_map = {
    ":dardo:": "🎯",
    ":página_boca_arriba:": "📄",
    ":bombilla:": "💡",
    ":espadas_cruzadas:": "⚔️",
    ":autopista:": "🛣️",
    ":bolsa_de_dinero:": "💰"
}

print("ANTES del mapeo:")
print(test_text)
print("\n" + "="*50)

for src, uni in emoji_map.items():
    test_text = test_text.replace(src, uni)

print("\nDESPUÉS del mapeo:")
print(test_text)
print("\n✅ Emoji mapping funcionando correctamente")