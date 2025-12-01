import unittest
from greek_phonology import count_syllables, g2p_greek, detect_stress_position

class TestExperimentalPhonology(unittest.TestCase):
    
    def test_synizesis_syllables(self):
        # παιδιά -> pe-dja (2 syllables, not 3)
        self.assertEqual(count_syllables("παιδιά"), 2, "παιδιά should be 2 syllables (synizesis)")
        
        # ποιος -> pjos (1 syllable)
        self.assertEqual(count_syllables("ποιος"), 1, "ποιος should be 1 syllable")
        
        # τέτοιος -> te-tjos (2 syllables)
        self.assertEqual(count_syllables("τέτοιος"), 2, "τέτοιος should be 2 syllables")
        
        # δουλειά -> du-lja (2 syllables)
        self.assertEqual(count_syllables("δουλειά"), 2, "δουλειά should be 2 syllables")
        
        # Contrast with stressed i:
        # θεία -> thi-a (2 syllables)
        self.assertEqual(count_syllables("θεία"), 2, "θεία should be 2 syllables")
        
        # τέτοιος -> te-tjos (2 syllables)
        self.assertEqual(count_syllables("τέτοιος"), 2, "τέτοιος should be 2 syllables")
        
    def test_specific_user_cases(self):
        # γάιδαρος -> ga-i-da-ros (4 syllables)
        # Accent on alpha breaks the digraph
        self.assertEqual(count_syllables("γάιδαρος"), 4, "γάιδαρος should be 4 syllables")
        
        # γαίδαρος (hypothetical) -> ge-da-ros (3 syllables)
        # Accent on iota keeps it as digraph
        self.assertEqual(count_syllables("γαίδαρος"), 3, "γαίδαρος should be 3 syllables")
        
        # καϊκι -> ka-i-ki (3 syllables)
        # Diaeresis forces separation
        self.assertEqual(count_syllables("καϊκι"), 3, "καϊκι should be 3 syllables")
        
        # θεϊκός -> the-i-kos (3 syllables)
        self.assertEqual(count_syllables("θεϊκός"), 3, "θεϊκός should be 3 syllables")

        # θεϊκός -> the-i-kos (3 syllables)
        self.assertEqual(count_syllables("θεϊκός"), 3, "θεϊκός should be 3 syllables")

    def test_flexible_syllables(self):
        from greek_phonology import get_possible_syllable_counts
        
        # τέτοιος -> {2, 3} (te-tjos vs te-ti-os)
        self.assertEqual(get_possible_syllable_counts("τέτοιος"), {2, 3})
        
        # παιδιά -> {2, 3} (pe-dja vs pe-di-a)
        self.assertEqual(get_possible_syllable_counts("παιδιά"), {2, 3})
        
        # γάιδαρος -> {4} (accent prevents synizesis)
        self.assertEqual(get_possible_syllable_counts("γάιδαρος"), {4})
        
        # καϊκι -> {3} (diaeresis prevents synizesis)
        self.assertEqual(get_possible_syllable_counts("καϊκι"), {3})

        # καϊκι -> {3} (diaeresis prevents synizesis)
        self.assertEqual(get_possible_syllable_counts("καϊκι"), {3})

    def test_flexible_stress(self):
        from greek_phonology import detect_stress_position
        
        # τέτοιος -> F2 (synizesis) AND F3 (diaeresis)
        options = detect_stress_position("τέτοιος")
        types = [t[1] for t in options]
        self.assertIn('F2', types)
        self.assertIn('F3', types)
        
        # παιδιά -> M (synizesis) AND M (diaeresis) - Always Oxytone!
        options = detect_stress_position("παιδιά")
        types = [t[1] for t in options]
        self.assertIn('M', types)
        # self.assertIn('F2', types) # Incorrect: stress is always on final 'ά'

    def test_vc_sequences(self):
        # αυτός -> af-tos (2 syllables)
        self.assertEqual(count_syllables("αυτός"), 2)
        self.assertIn("af", g2p_greek("αυτός"))
        
        # αύριο -> av-rjo (2 syllables with synizesis)
        self.assertEqual(count_syllables("αύριο"), 2)
        self.assertIn("av", g2p_greek("αύριο"))
        
        # ευχαριστώ -> ef-xa-ri-sto (4 syllables)
        self.assertEqual(count_syllables("ευχαριστώ"), 4)
        self.assertIn("ef", g2p_greek("ευχαριστώ"))
        
    def test_digraphs(self):
        # είναι -> i-ne (2 syllables)
        self.assertEqual(count_syllables("είναι"), 2)
        
        # ουρανός -> u-ra-nos (3 syllables)
        self.assertEqual(count_syllables("ουρανός"), 3)
        
    def test_stress_detection_with_synizesis(self):
        # παιδιά -> Oxytone (M)
        # Stress is on 'ά'. 'ι' is glide.
        options = detect_stress_position("παιδιά")
        # Should contain M
        types = [t[1] for t in options]
        self.assertIn('M', types, "παιδιά should allow Oxytone")
        
        # τέτοιος -> Paroxytone (F2)
        options = detect_stress_position("τέτοιος")
        types = [t[1] for t in options]
        self.assertIn('F2', types, "τέτοιος should allow Paroxytone")

if __name__ == '__main__':
    unittest.main()
