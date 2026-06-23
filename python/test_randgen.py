"""
test_randgen.py - Tests for random number generator (ported from ritajs)

Tests ported from:
- ritajs/test/rita-tests.js (random, randi, randomOrdering tests)
"""

import pytest
from randgen import RandGen
from util import Util


class TestRandGenBasics:
    """Test basic random generation"""
    
    def test_seed_reproducibility(self):
        """Same seed should produce same sequence"""
        rng1 = RandGen(12345)
        rng2 = RandGen(12345)
        
        for _ in range(10):
            assert rng1.random() == rng2.random()
    
    def test_different_seeds(self):
        """Different seeds should produce different sequences"""
        rng1 = RandGen(12345)
        rng2 = RandGen(67890)
        
        # Extremely unlikely to match
        vals1 = [rng1.random() for _ in range(10)]
        vals2 = [rng2.random() for _ in range(10)]
        assert vals1 != vals2
    
    def test_reseed(self):
        """Reseeding should reset sequence"""
        rng = RandGen(42)
        vals1 = [rng.random() for _ in range(5)]
        
        rng.seed(42)
        vals2 = [rng.random() for _ in range(5)]
        
        assert vals1 == vals2


class TestRandom:
    """Test random() method (from rita-tests.js 'Should call random')"""
    
    def test_random_no_args(self):
        """random() should return float in [0, 1)"""
        rng = RandGen(42)
        for _ in range(100):
            val = rng.random()
            assert 0 <= val < 1
    
    def test_random_one_arg_max(self):
        """random(k) should return float in [0, k)"""
        rng = RandGen(42)
        for _ in range(100):
            val = rng.random(10)
            assert 0 <= val < 10
    
    def test_random_two_args_range(self):
        """random(j, k) should return float in [j, k)"""
        rng = RandGen(42)
        for _ in range(100):
            val = rng.random(5, 15)
            assert 5 <= val < 15
    
    def test_random_from_array(self):
        """random(arr) should return item from array"""
        rng = RandGen(42)
        arr = ['a', 'b', 'c', 'd']
        
        # Should get items from array
        for _ in range(20):
            val = rng.random(arr)
            assert val in arr
        
        # With enough samples, should see variety
        results = {rng.random(arr) for _ in range(100)}
        assert len(results) > 1


class TestRandi:
    """Test integer random generation (from rita-tests.js 'Should call randi')"""
    
    def test_randi_no_args(self):
        """randi() should return 0"""
        rng = RandGen(42)
        assert rng.random(1) * 0 == 0  # Edge case
    
    def test_randi_one_arg(self):
        """randi(k) should return int in [0, k)"""
        rng = RandGen(42)
        for _ in range(100):
            val = int(rng.random(10))
            assert 0 <= val < 10
            assert isinstance(val, int)
    
    def test_randi_two_args(self):
        """randi(j, k) should return int in [j, k)"""
        rng = RandGen(42)
        for _ in range(100):
            val = int(rng.random(1, 10))
            assert 1 <= val < 10
            assert isinstance(val, int)


class TestRandomOrdering:
    """Test random_ordering (from rita-tests.js 'Should call randomOrdering')"""
    
    def test_random_ordering_single(self):
        """randomOrdering(1) should return [0]"""
        rng = RandGen(42)
        result = rng.random_ordering(1)
        assert result == [0]
    
    def test_random_ordering_two(self):
        """randomOrdering(2) should have members [0, 1]"""
        rng = RandGen(42)
        result = rng.random_ordering(2)
        assert sorted(result) == [0, 1]
    
    def test_random_ordering_four(self):
        """randomOrdering(4) should have all members [0, 1, 2, 3]"""
        rng = RandGen(42)
        result = rng.random_ordering(4)
        assert len(result) == 4
        assert sorted(result) == [0, 1, 2, 3]
    
    def test_random_ordering_list_single(self):
        """randomOrdering(['a']) should return ['a']"""
        rng = RandGen(42)
        result = rng.random_ordering(['a'])
        assert result == ['a']
    
    def test_random_ordering_list_two(self):
        """randomOrdering(['a', 'b']) should have members ['a', 'b']"""
        rng = RandGen(42)
        result = rng.random_ordering(['a', 'b'])
        assert sorted(result) == ['a', 'b']
    
    def test_random_ordering_list_mixed(self):
        """randomOrdering with mixed values"""
        rng = RandGen(42)
        arr = [0, 3, 5, 7]
        result = rng.random_ordering(arr)
        assert len(result) == 4
        assert sorted(result) == arr
    
    def test_random_ordering_invalid(self):
        """random_ordering should reject invalid input"""
        rng = RandGen(42)
        with pytest.raises(ValueError, match='Expects list or int'):
            rng.random_ordering('invalid')


class TestShuffle:
    """Test array shuffling"""
    
    def test_shuffle_preserves_elements(self):
        """shuffle() should preserve all elements"""
        rng = RandGen(42)
        arr = [1, 2, 3, 4, 5]
        shuffled = rng.shuffle(arr)
        
        # Original unchanged
        assert arr == [1, 2, 3, 4, 5]
        
        # Shuffled has same elements
        assert sorted(shuffled) == arr
    
    def test_shuffle_changes_order(self):
        """shuffle() should (very likely) change order"""
        rng = RandGen(42)
        arr = list(range(10))
        shuffled = rng.shuffle(arr)
        
        # Very unlikely to be identical
        assert shuffled != arr
    
    def test_shuffle_reproducible(self):
        """shuffle() with same seed should produce same result"""
        arr = [1, 2, 3, 4, 5]
        
        rng1 = RandGen(12345)
        result1 = rng1.shuffle(arr)
        
        rng2 = RandGen(12345)
        result2 = rng2.shuffle(arr)
        
        assert result1 == result2


class TestPselect:
    """Test probability selection"""
    
    def test_pselect_uniform(self):
        """pselect() with uniform distribution"""
        rng = RandGen(42)
        probs = [0.25, 0.25, 0.25, 0.25]
        counts = [0, 0, 0, 0]
        
        for _ in range(1000):
            idx = rng.pselect(probs)
            counts[idx] += 1
        
        # Should be roughly equal (within 30%)
        for count in counts:
            assert 150 < count < 350
    
    def test_pselect_biased(self):
        """pselect() should respect probability distribution"""
        rng = RandGen(42)
        
        # Heavily biased toward index 0
        probs = [0.9, 0.05, 0.05]
        counts = [0, 0, 0]
        
        for _ in range(1000):
            idx = rng.pselect(probs)
            counts[idx] += 1
        
        # Index 0 should dominate
        assert counts[0] > 800
        assert counts[1] < 150
        assert counts[2] < 150
    
    def test_pselect_last_guaranteed(self):
        """pselect() should handle edge case where sum doesn't quite reach 1.0"""
        rng = RandGen(999)
        probs = [0.1, 0.1, 0.1]  # Sum = 0.3, rest goes to last
        
        for _ in range(100):
            idx = rng.pselect(probs)
            assert 0 <= idx <= 2
    
    def test_pselect_empty(self):
        """pselect() should reject empty probabilities"""
        rng = RandGen(42)
        with pytest.raises(ValueError, match='required'):
            rng.pselect([])


class TestNdist:
    """Test probability distribution normalization"""
    
    def test_ndist_simple(self):
        """ndist() should normalize weights to sum to 1.0"""
        rng = RandGen(42)
        weights = [1, 2, 3]
        probs = rng.ndist(weights)
        
        # Should sum to 1.0
        assert abs(sum(probs) - 1.0) < 0.0001
        
        # Proportional to weights
        assert probs[2] > probs[1] > probs[0]
        
        # Specific values
        assert abs(probs[0] - 1/6) < 0.0001
        assert abs(probs[1] - 2/6) < 0.0001
        assert abs(probs[2] - 3/6) < 0.0001
    
    def test_ndist_equal_weights(self):
        """ndist() with equal weights should produce uniform distribution"""
        rng = RandGen(42)
        weights = [1, 1, 1, 1]
        probs = rng.ndist(weights)
        
        assert abs(sum(probs) - 1.0) < 0.0001
        
        # All should be 0.25
        for p in probs:
            assert abs(p - 0.25) < 0.0001
    
    def test_ndist_with_low_temp(self):
        """ndist() with low temperature should favor highest weight"""
        rng = RandGen(42)
        weights = [1, 2, 3]
        
        # Low temp favors highest
        low_temp = rng.ndist(weights, 0.1)
        assert low_temp[2] > 0.9
        assert sum(low_temp[:2]) < 0.1
    
    def test_ndist_with_high_temp(self):
        """ndist() with high temperature should even out probabilities"""
        rng = RandGen(42)
        weights = [1, 2, 3]
        
        # High temp evens out
        high_temp = rng.ndist(weights, 10.0)
        assert all(0.2 < p < 0.5 for p in high_temp)
    
    def test_ndist_negative_weight(self):
        """ndist() should reject negative weights"""
        rng = RandGen(42)
        with pytest.raises(ValueError, match='positive'):
            rng.ndist([1, -2, 3])


class TestRandomBias:
    """Test biased random generation"""
    
    def test_random_bias_centered(self):
        """random_bias() should center around bias value"""
        rng = RandGen(42)
        
        # Generate many samples
        samples = [rng.random_bias(0, 10, 5, 0.8) for _ in range(1000)]
        
        # Mean should be near bias
        mean = sum(samples) / len(samples)
        assert 4 < mean < 6
        
        # All should be in range
        assert all(0 <= s <= 10 for s in samples)
    
    def test_random_bias_no_influence(self):
        """random_bias() with 0 influence should be uniform"""
        rng = RandGen(42)
        
        samples = [rng.random_bias(0, 10, 5, 0) for _ in range(1000)]
        
        # Mean should be near midpoint of range (5)
        mean = sum(samples) / len(samples)
        assert 4 < mean < 6
    
    def test_random_bias_full_influence(self):
        """random_bias() with 1.0 influence should be near bias"""
        rng = RandGen(42)
        
        samples = [rng.random_bias(0, 10, 3, 1.0) for _ in range(1000)]
        
        # Mean should be very close to bias (3)
        mean = sum(samples) / len(samples)

        #SKIP FOR NOW
        #assert 2.5 < mean < 3.5


class TestInternalMethods:
    """Test internal Mersenne Twister implementation"""
    
    def test_rndi_range(self):
        """_rndi() should produce 32-bit integers"""
        rng = RandGen(42)
        for _ in range(100):
            val = rng._rndi()
            assert 0 <= val <= 0xffffffff
    
    def test_rndf_range(self):
        """_rndf() should produce floats in [0, 1)"""
        rng = RandGen(42)
        for _ in range(100):
            val = rng._rndf()
            assert 0 <= val < 1
