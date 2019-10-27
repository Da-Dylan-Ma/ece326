import unittest
from easybj import *

class TestHandMethods(unittest.TestCase):

    def setUp(self):
        ### PLAYER ###
        # 21-value hands
        self.h_at = Hand("AT")
        self.h_ta = Hand("TA")
        self.h_tta = Hand("TTA")

        # split hands
        self.h_aa = Hand("AA")
        self.h_22 = Hand("22")
        self.h_55 = Hand("55")
        self.h_tt = Hand("TT")

        # hard hands
        self.h_23 = Hand("23")
        self.h_236 = Hand("236")
        self.h_t9 = Hand("T9")
        self.h_a84 = Hand("A84")
        self.h_65 = Hand("65")
        self.h_89 = Hand("89")

        # soft hands
        self.h_a6 = Hand("A6")
        self.h_a7 = Hand("A7")
        self.h_a8 = Hand("A8")
        self.h_8a = Hand("8A")
        self.h_44a = Hand("44A")
        self.h_aaaa = Hand("AAAA")

        # busted hands
        self.h_t4a7 = Hand("T4A7")
        self.h_t68 = Hand("T68")

        ### DEALER ###
        # 21-value hands
        self.d_at = Hand("AT", dealer=True)
        self.d_ta = Hand("TA", dealer=True)
        self.d_tta = Hand("TTA", dealer=True)

        # hard hands
        self.d_22 = Hand("22", dealer=True)
        self.d_55 = Hand("55", dealer=True)
        self.d_tt = Hand("TT", dealer=True)
        self.d_23 = Hand("23", dealer=True)
        self.d_236 = Hand("236", dealer=True)
        self.d_t9 = Hand("T9", dealer=True)
        self.d_a84 = Hand("A84", dealer=True)
        self.d_65 = Hand("65", dealer=True)
        self.d_89 = Hand("89", dealer=True)
        self.d_a7 = Hand("A7", dealer=True)
        self.d_a8 = Hand("A8", dealer=True)
        self.d_8a = Hand("8A", dealer=True)
        self.d_44a = Hand("44A", dealer=True)

        # soft hands
        self.d_aa = Hand("AA", dealer=True)
        self.d_a6 = Hand("A6", dealer=True)
        self.d_aaaa = Hand("AAAA", dealer=True)

        # busted hands
        self.d_t4a7 = Hand("T4A7", dealer=True)
        self.d_t68 = Hand("T68", dealer=True)

    def test_code(self):
        _ = self.assertEqual

        # player
        _(self.h_at.code(), "BJ")
        _(self.h_ta.code(), "BJ")
        _(self.h_tta.code(), "21")
        _(self.h_aa.code(), "AA")
        _(self.h_22.code(), "22")
        _(self.h_55.code(), "55")
        _(self.h_tt.code(), "TT")
        _(self.h_aa.code(nosplit=True), "AA")
        _(self.h_22.code(nosplit=True), "4")
        _(self.h_55.code(nosplit=True), "10")
        _(self.h_tt.code(nosplit=True), "20")
        _(self.h_23.code(nosplit=True), "5")
        _(self.h_23.code(), "5")
        _(self.h_236.code(), "11")
        _(self.h_t9.code(), "19")
        _(self.h_a84.code(), "13")
        _(self.h_65.code(), "11")
        _(self.h_89.code(), "17")
        _(self.h_a6.code(), "A6")
        _(self.h_a7.code(), "A7")
        _(self.h_a8.code(), "A8")
        _(self.h_8a.code(), "A8")
        _(self.h_44a.code(), "A8")
        _(self.h_aaaa.code(), "A3")
        _(self.h_t4a7.code(), BUST_CODE)
        _(self.h_t68.code(), BUST_CODE)

        # dealer
        _(self.d_at.code(), "BJ")
        _(self.d_ta.code(), "BJ")
        _(self.d_tta.code(), "21")
        _(self.d_aa.code(), "AA")
        _(self.d_22.code(), "4")
        _(self.d_55.code(), "10")
        _(self.d_tt.code(), "20")
        _(self.d_aa.code(nosplit=True), "AA")
        _(self.d_22.code(nosplit=True), "4")
        _(self.d_55.code(nosplit=True), "10")
        _(self.d_tt.code(nosplit=True), "20")
        _(self.d_23.code(nosplit=True), "5")
        _(self.d_23.code(), "5")
        _(self.d_236.code(), "11")
        _(self.d_t9.code(), "19")
        _(self.d_a84.code(), "13")
        _(self.d_65.code(), "11")
        _(self.d_a6.code(), "A6")
        _(self.d_a7.code(), "18")
        _(self.d_a8.code(), "19")
        _(self.d_8a.code(), "19")
        _(self.d_89.code(), "17")
        _(self.d_44a.code(), "19")
        _(self.d_aaaa.code(), "A3")
        _(self.d_t4a7.code(), BUST_CODE)
        _(self.d_t68.code(), BUST_CODE)

    def test_value(self):
        _ = self.assertEqual

        _(self.h_at.value(), 21)
        _(self.h_ta.value(), 21)
        _(self.h_tta.value(), 21)
        _(self.h_aa.value(), 12)
        _(self.h_22.value(), 4)
        _(self.h_55.value(), 10)
        _(self.h_tt.value(), 20)
        _(self.d_23.value(), 5)
        _(self.d_236.value(), 11)
        _(self.d_t9.value(), 19)
        _(self.d_a84.value(), 13)
        _(self.d_65.value(), 11)
        _(self.d_89.value(), 17)
        _(self.d_a6.value(), 17)
        _(self.d_a7.value(), 18)
        _(self.d_a8.value(), 19)
        _(self.d_8a.value(), 19)
        _(self.d_44a.value(), 19)
        _(self.d_aaaa.value(), 14)
        _(self.d_t4a7.value(), BUST)
        _(self.d_t68.value(), BUST)


if __name__ == "__main__":
    unittest.main()
