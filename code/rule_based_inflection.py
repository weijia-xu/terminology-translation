from collections import defaultdict


def inflect(tgt_lang, src_sentence, src_terms, tgt_lemmas, lemma_tag_to_form):
	if tgt_lang == "de":
		return inflect_de(src_sentence, src_terms, tgt_lemmas, lemma_tag_to_form)
	elif tgt_lang == "lt":
		return inflect_lt(src_sentence, src_terms, tgt_lemmas, lemma_tag_to_form)


def inflect_de(src_sentence, src_terms, tgt_lemmas, lemma_tag_to_form):
	adj_degree_map = {"POS": "pos", "Cmp": "comp", "Sup": "sup"}
	number_map = {"Sing": "sing", "Plur": "plu"}
	person_map = {"1": "1per", "2": "2per", "3": "3per"}
	tense_map = {"Pres": "pres", "Past": "past"}

	id_to_node = dict()
	word_to_node = dict()
	head_nodes = dict()
	children_nodes = defaultdict(dict)
	for sentence in src_sentence.sentences:
		for word in sentence.words:
			nid = word.id
			deprel = word.deprel
			id_to_node[nid] = word
			head_nodes[nid] = word.head
			children_nodes[word.head][deprel] = nid
			if word.text not in word_to_node:
				word_to_node[word.text] = word

	tgt_terms = []
	for src_term, tgt_lemma_term in zip(src_terms, tgt_lemmas):
		case = "nom"
		number = "sing"
		adj_degree = "pos"
		person = "3per"
		tense = "pres"
		mood = "ind"
		# determine adjective degree
		if len(tgt_lemma_term.split()) > 1:
			src_first = src_term.split()[0].strip()
			word = word_to_node[src_first]
			if word.upos == "ADJ" and word.feats:	
				for feat in word.feats.split("|"):
					if feat.startswith("Degree="):
						adj_degree = adj_degree_map[feat[len("Degree="):]]

		src_last = src_term.split()[-1].strip()
		if src_last not in word_to_node:
			tgt_terms.append(tgt_lemma_term)
			continue
		word = word_to_node[src_last]
		if word.upos in ["PROPN", "NOUN", "ADJ", "ADV"] or (word.upos == "VERB" and word.deprel == "amod"):
			# determine case
			root_word = word
			while root_word.deprel in ["flat", "amod", "advmod", "appos", "compound"]:
				root_word = id_to_node[head_nodes[root_word.id]]
			if root_word.deprel == ["nsubj", "root", "csubj", "acl", "nsubj:pass", "csubj:pass"]:
				case = "nom"
			elif root_word.deprel in ["obj", "dobj"]:
				if root_word.deprel == "obj" and id_to_node[head_nodes[root_word.id]].text == "using":
					case = "dat"
				else:
					case = "acc"
			elif root_word.deprel == "nmod":
				if id_to_node[head_nodes[root_word.id]].lemma in ["by", "to", "against", "without", "for"]:
					case = "acc"
				else:
					case = "dat"
			elif root_word.deprel == "nmod:poss":
				case = "gen"
			elif root_word.deprel in ["iobj", "obl"] or root_word.deprel.startswith("nmod"):
				case = "dat"
			# determine number
			mod_root_word = word
			while mod_root_word.deprel in ["amod", "advmod"]:
				mod_root_word = id_to_node[head_nodes[mod_root_word.id]]
			if mod_root_word.feats:
				for feat in mod_root_word.feats.split("|"):
					if feat.startswith("Number="):
						number = number_map[feat[len("Number="):]]
			if number == "sing" and mod_root_word.lemma in ["pain", "food"]:
				number = "plu"
			# inflect target term
			tgt_term = []
			for tgt_lemma in tgt_lemma_term.split():
				tgt_word = tgt_lemma
				if word.upos in ["ADJ", "VERB"]:
					if number == "plu":
						tgt_word = tgt_lemma + "en"
					elif case in ["nom", "acc"]:
						tgt_word = tgt_lemma + "e"
					else:
						tgt_word = tgt_lemma + "en"
				elif tgt_lemma in lemma_tag_to_form:
					pos = "NN"
					for gender in ["noGender", "masc", "neut", "fem"]:
						form = ",".join([pos, gender, case, number])
						if form in lemma_tag_to_form[tgt_lemma]:
							tgt_word = lemma_tag_to_form[tgt_lemma][form]
				if number == "plu":
					if tgt_lemma.endswith("ung") or tgt_lemma.endswith("tion"):
						tgt_word = tgt_lemma + "en"
				tgt_term.append(tgt_word)
			tgt_terms.append(" ".join(tgt_term))
		elif word.upos == "VERB":
			if "nsubj" in children_nodes[word.id]:
				subj = id_to_node[children_nodes[word.id]["nsubj"]]
				# determine person
				if subj.upos == "PRON" and subj.feats:
					for feat in subj.feats.split("|"):
						if feat.startswith("Person="):
							person = person_map[feat[len("Person="):]]
				# determine number
				if subj.feats:
					for feat in subj.feats.split("|"):
						if feat.startswith("Number="):
							number = number_map[feat[len("Number="):]]
			else:
				person = "2per"
				number = "plu"
			# determine mood
			if "Mood=Sub" in word.feats:
				mood = "subj"
			else:
				mood = "ind"
			# determine tense
			for feat in word.feats.split("|"):
				if feat.startswith("Tense="):
					tense = tense_map[feat[len("Tense="):]]
			# inflect target term
			tgt_term = []
			for tgt_lemma in tgt_lemma_term.split():
				tgt_word = tgt_lemma
				if tgt_lemma in lemma_tag_to_form:
					pos = "V"
					form = ",".join([pos, person, number, tense, mood])
					if form in lemma_tag_to_form[tgt_lemma]:
						tgt_word = lemma_tag_to_form[tgt_lemma][form]
				tgt_term.append(tgt_word)
			tgt_terms.append(" ".join(tgt_term))
	return tgt_terms


def inflect_lt(src_sentence, src_terms, tgt_lemmas, lemma_tag_to_form):
	adj_degree_map = {"POS": "positive", "Cmp": "comparative", "Sup": "superlative"}
	number_map = {"Sing": "singular", "Plur": "plural"}
	person_map = {"1": "first-person", "2": "second-person", "3": "third-person"}
	tense_map = {"Pres": "present", "Past": "past"}

	id_to_node = dict()
	word_to_node = dict()
	head_nodes = dict()
	children_nodes = defaultdict(dict)
	for sentence in src_sentence.sentences:
		for word in sentence.words:
			nid = word.id
			deprel = word.deprel
			id_to_node[nid] = word
			head_nodes[nid] = word.head
			children_nodes[word.head][deprel] = nid
			if word.text not in word_to_node:
				word_to_node[word.text] = word

	tgt_terms = []
	for src_term, tgt_lemma_term in zip(src_terms, tgt_lemmas):
		case = "nominative"
		number = "singular"
		adj_degree = "positive"
		person = "third-person"
		tense = "present"
		if len(tgt_lemma_term.split()) > 1:
			src_first = src_term.split()[0].strip()
			word = word_to_node[src_first]
			if word.upos == "ADJ":	
				for feat in word.feats.split("|"):
					if feat.startswith("Degree="):
						adj_degree = adj_degree_map[feat[len("Degree="):]]

		src_last = src_term.split()[-1].strip()
		word = word_to_node[src_last]
		if word.upos in ["PROPN", "NOUN", "ADJ"]:
			# determine case
			root_word = word
			while root_word.deprel in ["flat", "amod", "advmod", "appos"]:
				root_word = id_to_node[head_nodes[root_word.id]]
			if root_word.deprel == ["nsubj", "root", "csubj", "acl", "nsubj:pass", "csubj:pass"]:
				case = "nominative"
			elif head_nodes[root_word.id] and id_to_node[head_nodes[root_word.id]].lemma in ["be", "have", "like", "feel"]:
				case = "nominative"
			elif root_word.deprel in ["obj", "dobj"]:
				case = "accusative"
			elif root_word.deprel == "iobj":
				case = "dative"
			elif root_word.deprel.startswith("nmod") or root_word.deprel in ["obl", "compound"]:
				if "case" in children_nodes[root_word.id]:
					child = id_to_node[children_nodes[root_word.id]["case"]]
					if child.lemma in ["by", "with", "through"]:
						case = "instrumental"
					elif child.upos == "ADP" and child.lemma not in ["of", "from", "to"]:
						case = "locative"
					else:
						case = "genitive"
				else:
					case = "genitive"
			# determine number
			mod_root_word = word
			while mod_root_word.deprel in ["amod", "advmod"]:
				mod_root_word = id_to_node[head_nodes[mod_root_word.id]]
			for feat in mod_root_word.feats.split("|"):
				if feat.startswith("Number="):
					number = number_map[feat[len("Number="):]]
			if number == "singular" and root_word.deprel == "nsubj":
				head = id_to_node[head_nodes[root_word.id]]
				if head.text in ["are", "were"]:
					number = "plural"
			elif number == "singular" and root_word.deprel in ["ccomp", "acl", "root"]:
				if "cop" in children_nodes[root_word.id]:
					child = id_to_node[children_nodes[root_word.id]["cop"]]
					if child.text in ["are", "were"]:
						number = "plural"
			# inflect target term
			tgt_term = []
			for tgt_lemma in tgt_lemma_term.split():
				tgt_word = tgt_lemma
				if tgt_lemma in lemma_tag_to_form:
					for pos in ["NN", "ADJ"]:
						for gender in ["feminine", "masculine"]:
							if pos == "ADJ":
								form = ",".join([pos] + sorted([gender, number, case, adj_degree]))
							else:
								form = ",".join([pos] + sorted([gender, number, case]))
							if form in lemma_tag_to_form[tgt_lemma]:
								tgt_word = lemma_tag_to_form[tgt_lemma][form]
				tgt_term.append(tgt_word)
			tgt_terms.append(" ".join(tgt_term))
		elif word.upos == "VERB":
			if "nsubj" in children_nodes[word.id]:
				subj = id_to_node[children_nodes[word.id]["nsubj"]]
				# determine person
				if subj.upos == "PRON":
					for feat in subj.feats.split("|"):
						if feat.startswith("Person="):
							person = person_map[feat[len("Person="):]]
				# determine number
				for feat in subj.feats.split("|"):
					if feat.startswith("Number="):
						number = number_map[feat[len("Number="):]]
			else:
				person = "second-person"
				number = "plural"
			# determine tense
			if "Mood=Sub" in word.feats:
				tense = "subjunctive"
			elif "Mood=Imp" in word.feats:
				tense = "imperative"
			else:
				for feat in word.feats.split("|"):
					if feat.startswith("Tense="):
						tense = tense_map[feat[len("Tense="):]]
			# inflect target term
			tgt_term = []
			for tgt_lemma in tgt_lemma_term.split():
				tgt_word = tgt_lemma
				if tgt_lemma in lemma_tag_to_form:
					pos = "V"
					form = ",".join([pos] + sorted([person, number, tense]))
					if form in lemma_tag_to_form[tgt_lemma]:
						tgt_word = lemma_tag_to_form[tgt_lemma][form]
				tgt_term.append(tgt_word)
			tgt_terms.append(" ".join(tgt_term))
	return tgt_terms