## Explorer AI's chabot model

Explorer AI's dialog management and predictive abilities are facilitated by [Rasa](https://rasa.com/), an open source 
platform for chatbot development. The bot's domain (the list of user intents to classify, the types of important 
information to identify, the list of responses or actions to choose from) is specified in `rasa/domain.yml`, and the 
details of its model's pipeline and policy configurations are given in `rasa/config.yml`. These files provide high-level 
descriptions of the chatbot's intended dialog turns and learning algorithm, respectively.

Explorer AI's chatbot functionality has the following major components:
 - **Intent classification.** When the user types a message, the bot should classify the user's intention 
(e.g. asking for information about an exhibit).
 - **Entity extraction.** For certain user intents, the bot should recognize and extract important information 
(e.g. the name of the exhibit).
 - **Information storage.** Sometimes the bot should save extracted entities in slots for use in future responses or 
custom actions..
 - **State tracking.** The bot should keep track of the current status of the dialog (i.e. it should remember recent 
conversation history).
 - **Policy prediction.** The bot should use rules, stories, and conversation history to predict the most appropriate 
action to take at each of its turns.
 - **Action taking.** After prediction, the bot should typically respond to the user somehow; the content of its 
response is often the result of a custom action.

---

Explorer AI's **intent classifier** is trained with a relatively small collection of
(manually-entered) labeled training examples, which can be found in the following files:
 - `rasa/data/nlu/*.yml`
 - `rasa/data/nlu/exhibits/*.yml` 
 - `rasa/data/nlu/subjects/*.yml`

Annotations in the training data, like so
```
# in ask_about_exhibit.yml
- can you tell me how [coupled pendulums](exhibit) works?

 # in ask_for_explanation.yml
- i want to learn about [orthographic projection](subject)
```
provide Explorer AI's **entity extractor** with examples for how the entities `exhibit` and `subject` will typically 
appear in a user's message. On the other hand, the entity `NAME` is extracted with the help of a Spacy pre-trained 
model (see `rasa/config.yml`).

Explorer AI's **policy prediction** is trained with a combination of `rules` and `stories` (both contained in 
`rasa/data/`), which teach the bot how conversations should flow. Rules are short, deterministic, and are always 
followed. On the other hand, stories are (usually longer) training examples which have the ability to generalize to 
unobserved dialog paths. Having a combination of both types of training data makes the policy predictor robust.

Explorer AI's custom actions are defined in `rasa/actions/actions.py`. The bot's custom actions are responsible for not 
only generating and delivering its responses, but also performing background tasks like running scripts, querying 
databases, calling APIs, and managing memory (slots).
