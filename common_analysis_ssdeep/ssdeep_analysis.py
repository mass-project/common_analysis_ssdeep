from common_analysis_base import AnalysisPluginString
from collections import defaultdict
import ssdeep
import time
import logging
from . import __version__

log = logging.getLogger(__name__)

system_version = __version__

def n_grams(sequence,n=7):
    for i in range(len(sequence)-(n-1)):
        yield sequence[i:i+n]


class SsdeepHash:
    def __init__(self, identifier, ssdeep_hash):
        self.identifier = identifier
        self.hash_value = ssdeep_hash
        ssdeep_hash_parts = ssdeep_hash.split(':')
        self.chunk_size = int(ssdeep_hash_parts[0])
        self.chunk = ssdeep_hash_parts[1]
        self.double_chunk = ssdeep_hash_parts[2] 

    def __hash__(self):
        return hash(self.hash_value)

    def __eq__(self, other):
        return self.identifier == other.identifier

    def compare(self, other):
        return ssdeep.compare(self.hash_value, other.hash_value)


class CommonAnalysisSsdeep(AnalysisPluginString):
    def __init__(self, init_cache_data=None):
        super(CommonAnalysisSsdeep, self).__init__(system_version)
        self.cache = dict()
        self.chunk_sizes = defaultdict(set)
        self.chunks = defaultdict(set)
        self.double_chunks = defaultdict(set)
        if init_cache_data:
            start_load_cache_time = time.time()
            log.info('Initialize ssdeep cache.')
            self._load_cache(init_cache_data)
            end_load_cache_time = time.time()
            log.info('Cache initialized in {}sec'.format(end_load_cache_time - start_load_cache_time))

    def _add_to_cache(self, ssdeep_hash):
        self.cache[ssdeep_hash.identifier] = ssdeep_hash
        self.chunk_sizes[ssdeep_hash.chunk_size].add(ssdeep_hash)
        for part in n_grams(ssdeep_hash.chunk):
            self.chunks[part].add(ssdeep_hash)
        for part in n_grams(ssdeep_hash.double_chunk):
            self.double_chunks[part].add(ssdeep_hash)

    def _load_cache(self, init_data):
        for identifier, hash_value in init_data.items():
            new_ssdeep_hash = SsdeepHash(identifier, hash_value)
            self._add_to_cache(new_ssdeep_hash)

    def _candidates_same_length(self, sample_ssdeep_hash):
        same_length = set()
        same_length = same_length.union(self.chunk_sizes[sample_ssdeep_hash.chunk_size])
        same_length = same_length.union(self.chunk_sizes[sample_ssdeep_hash.chunk_size*2])
        if sample_ssdeep_hash.chunk_size % 2 == 0:
            same_length = same_length.union(self.chunk_sizes[sample_ssdeep_hash.chunk_size/2])
        return same_length

    def _candidates_common_chunks(self, sample_ssdeep_hash):
        same_chunks = set()
        for part in n_grams(sample_ssdeep_hash.chunk):
            same_chunks = same_chunks.union(self.chunks[part])
        for part in n_grams(sample_ssdeep_hash.double_chunk):
            same_chunks = same_chunks.union(self.double_chunks[part])
        return same_chunks

    def _generate_candidates(self, sample_ssdeep_hash):
        same_length = self._candidates_same_length(sample_ssdeep_hash)
        common_chunks = self._candidates_common_chunks(sample_ssdeep_hash)
        candidates = same_length & common_chunks
        log.info('Generated {} candidates ({} saved)'.format(len(candidates), len(self.cache) - len(candidates)))
        return candidates

    def analyze_string(self, ssdeep_hash, identifier=''):
        """
        Find identifier with similar ssdeep hash.
        The field 'similar samples' of the report contains a list of all
        identifiers which are similar, i.e. have a compare value greater 0. The
        list is of the form [(id1, comp_val1), (id2, comp_val2), ... ]

        :param str ssdeep_hash: SSDeep Hash value
        :param identifier: Unique identifier to identify the ssdeep hash. Required if hash value should be added to cache.
        :type identifier: str or None
        :returns: Report dictionary.         :rtype: dict
        """
        similar_samples = list()
        sample_ssdeep_hash = SsdeepHash(identifier, ssdeep_hash)
        candidates = self._generate_candidates(sample_ssdeep_hash)
        for candidate in candidates:
            compare_value = sample_ssdeep_hash.compare(candidate)
            if compare_value > 0 and sample_ssdeep_hash != candidate:
                similar_samples.append((candidate.identifier, compare_value))
        if not identifier:
            self.cache[identifier] = sample_ssdeep_hash

        result = self.prepare_analysis_report_dictionary()
        result['similar samples'] = similar_samples
        return result
