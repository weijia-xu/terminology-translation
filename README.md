# Rule-based Morphological Inflection Improves Neural Terminology Translation
Data and source code for the EMNLP (2021) paper:

[**Rule-based Morphological Inflection Improves Neural Terminology Translation**](https://arxiv.org/abs/2109.04620)

Weijia Xu, Marine Carpuat

## Test Suites
We construct two test suites ``en-de.health.tagged`` and ``en-lt.news.tagged`` to evaluate MT with lemma terminology constraints in domain adaptation and low-resource settings, respectively.

## Code
We release the code for rule-based inflection in ``code/rule_based_inflection.py``. It provides an ``inflect`` function that takes the following arguments:
- ``tgt_lang``: language code of the target language (e.g. de for German and lt for Lithuanian)
- ``src_sentence``: source sentence in a string
- ``src_terms``: a list of source terms corresponding to each target lemma
- ``tgt_lemmas``: a list of target lemmas to be inflected (should have the same length as ``src_terms``)
- ``lemma_tag_to_form``: a dictionary of dictionaries that maps a target lemma given a morphological tag to the inflected form. As an example, it may like this:
```
{
	"run": {
		"V,1per,plu,pres,ind": run,
		"V,1per,plu,past,ind": ran,
	},
	"point": {
		"NN,noGender,nom,sing": "point",
		"NN,noGender,nom,plu": "points"
	}
}
```
For German, we extract the dictionary from [the German Morphological Dictionaries](https://github.com/DuyguA/german-morph-dictionaries). For Lithuanian, we use [UniMorph](https://unimorph.github.io/).