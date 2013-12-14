<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<title>Word Generator</title>
<link rel="stylesheet" type="text/css" href="words_view.css"/>
<!--<script src="//ajax.googleapis.com/ajax/libs/jquery/1.10.2/jquery.min.js"></script>-->

</head>
<body>
	<div id="form_container">
	
		<h1><a>Random Word Generator!</a></h1>
		<form method="post" action="/words">
		    <div class="form_description">
			<p>Specify the kind of word you want to generate!.</p>
		</div>						
			<ul >
			
					<li id="li_1" >
		<label class="description" for="partofspeech">Part of Speech </label>
		<span>
			<input id="element_1_1" name="partofspeech" class="element radio" type="radio" value="verb" />
<label class="choice" for="element_1_1">Verb</label>
<input id="element_1_2" name="partofspeech" class="element radio" type="radio" value="noun" />
<label class="choice" for="element_1_2">Noun</label>
<input id="element_1_3" name="partofspeech" class="element radio" type="radio" value="adjective" />
<label class="choice" for="element_1_3">Adjective</label>
<input id="element_1_4" name="partofspeech" class="element radio" type="radio" value="adverb" />
<label class="choice" for="element_1_4">Adverb</label>
<input id="element_1_5" name="partofspeech" class="element radio" type="radio" value="connective" />
<label class="choice" for="element_1_5">Conjunction (Connective)</label>

		</span> 
		</li>		<li id="li_5" >
		<label class="description" for="judgmental">Is the word judgmental? </label>
		<span>
			<input id="element_5_1" name="judgmental" class="element radio" type="radio" value="0" />
<label class="choice" for="element_5_1">Not judgmental</label>
<input id="element_5_2" name="judgmental" class="element radio" type="radio" value="1" />
<label class="choice" for="element_5_2">Positive</label>
<input id="element_5_3" name="judgmental" class="element radio" type="radio" value="-1" />
<label class="choice" for="element_5_3">Negative</label>

		</span> 
		</li>		<li id="li_2" >
		<label class="description" for="transitive">Should the verbs be transitive? </label>
		<span>
			<input id="element_2_1" name="transitive" class="element checkbox" type="checkbox" value="1" />
<label class="choice" for="element_2_1">Yes</label>

		</span> 
		</li>		<li id="li_3" >
		<label class="description" for="countable">Should the nouns be countable? </label>
		<span>
			<input id="element_3_1" name="countable" class="element checkbox" type="checkbox" value="1" />
<label class="choice" for="element_3_1">Yes</label>

		</span> 
		</li>		<li id="li_4" >
		<label class="description" for="hedge">Should the adverbs be hedging? </label>
		<span>
			<input id="element_4_1" name="hedge" class="element checkbox" type="checkbox" value="1" />
<label class="choice" for="element_4_1">Yes</label>

		</span> 
		</li>		<li id="li_5" >
		<label class="description" for="count">How many words should be generated?</label>
		<span>
			<input id="element_5_1" name="count" class="element text" type="text" placeholder="0" />
		</span> 
		</li>
			
				<input id="saveForm" class="button_text" type="submit" name="submit" value="Submit" />
			</ul>
		</form>	
	</div>
	</body>
</html>
