import unittest
from easybj import *

class TestHandMethods(unittest.TestCase):

    def setUp(self):
        ### PLAYER ###
        # 21-value hands
        self.h_at = Hand("A", "T")
        self.h_ta = Hand("T", "A")
        self.h_tta = Hand("T", "T")
        self.h_tta.cards.append("A")

        # split hands
        self.h_aa = Hand("A", "A")
        self.h_22 = Hand("2", "2")
        self.h_55 = Hand("5", "5")
        self.h_tt = Hand("T", "T")

        # hard hands
        self.h_23 = Hand("2", "3")
        self.h_236 = Hand("2", "3")
        self.h_236.cards.append("6")
        self.h_t9 = Hand("T", "9")
        self.h_a84 = Hand("A", "8")
        self.h_a84.cards.append("4")
        self.h_65 = Hand("6", "5")
        self.h_89 = Hand("8", "9")

        # soft hands
        self.h_a6 = Hand("A", "6")
        self.h_a7 = Hand("A", "7")
        self.h_a8 = Hand("A", "8")
        self.h_8a = Hand("8", "A")
        self.h_44a = Hand("4", "4")
        self.h_44a.cards.append("A")
        self.h_aaaa = Hand("A", "A")
        self.h_aaaa.cards.extend(["A", "A"])

        # busted hands
        self.h_t4a7 = Hand("T", "4")
        self.h_t4a7.cards.extend(["A", "7"])
        self.h_t68 = Hand("T", "6")
        self.h_t68.cards.append("8")

        ### DEALER ###
        # 21-value hands
        self.d_at = Hand("A", "T", dealer=True)
        self.d_ta = Hand("T", "A", dealer=True)
        self.d_tta = Hand("T", "T", dealer=True)
        self.d_tta.cards.append("A")

        # split hands
        self.d_aa = Hand("A", "A", dealer=True)
        self.d_22 = Hand("2", "2", dealer=True)
        self.d_55 = Hand("5", "5", dealer=True)
        self.d_tt = Hand("T", "T", dealer=True)

        # hard hands
        self.d_23 = Hand("2", "3", dealer=True)
        self.d_236 = Hand("2", "3", dealer=True)
        self.d_236.cards.append("6")
        self.d_t9 = Hand("T", "9", dealer=True)
        self.d_a84 = Hand("A", "8", dealer=True)
        self.d_a84.cards.append("4")
        self.d_65 = Hand("6", "5", dealer=True)
        self.d_a7 = Hand("A", "7", dealer=True)
        self.d_a8 = Hand("A", "8", dealer=True)
        self.d_8a = Hand("8", "A", dealer=True)
        self.d_89 = Hand("8", "9", dealer=True)
        self.d_44a = Hand("4", "4", dealer=True)
        self.d_44a.cards.append("A")

        # soft hands
        self.d_a6 = Hand("A", "6", dealer=True)
        self.d_aaaa = Hand("A", "A", dealer=True)
        self.d_aaaa.cards.extend(["A", "A"])

        # busted hands
        self.d_t4a7 = Hand("T", "4", dealer=True)
        self.d_t4a7.cards.extend(["A", "7"])
        self.d_t68 = Hand("T", "6", dealer=True)
        self.d_t68.cards.append("8")

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
        _(self.h_t4a7.code(), BUST)
        _(self.h_t68.code(), BUST)

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
        _(self.d_t4a7.code(), BUST)
        _(self.d_t68.code(), BUST)


if __name__ == "__main__":
    unittest.main()
