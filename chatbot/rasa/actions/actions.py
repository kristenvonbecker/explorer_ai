from rasa_sdk.events import SlotSet, SessionStarted, ActionExecuted, BotUttered
from rasa_sdk import Action, Tracker
from rasa_sdk import Tracker, ValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

from typing import Any, Text, Dict, List
import logging
import random

from .explanation_scripts import *
from .exhibit_scripts import *


logger = logging.getLogger(__name__)


exhibit_intents = ["ask_about_exhibit",
                   "ask_exhibit_creator",
                   "ask_exhibit_date",
                   "ask_where_exhibit",
                   "ask_related_exhibit"
                   ]


class ValidateSlots(ValidationAction):
    def validate_user_name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        name = next(tracker.get_latest_entity_values("PERSON"), None)
        last_intent = tracker.latest_message["intent"].get("name")
        if name and last_intent == "chit_chat/greet":
            return {"user_name": name}
        else:
            return {"user_name": None}

    def validate_name_given(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        name = tracker.get_slot("user_name")
        if name:
            return {"name_given": True}
        else:
            return {"name_given": False}


class ActionGetArticleMatches(Action):
    def name(self) -> Text:
        return "action_get_article_matches"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict) -> List[Dict[Text, Any]]:
        subject = tracker.get_slot("subject")
        matches = []
        if subject:
            matches += get_article_matches(subject)
        matches_available = True if matches else False
        return [
            SlotSet("exhibit_id", None),
            SlotSet("num_tries", 0),
            SlotSet("article_matches", matches),
            SlotSet("matches_available", matches_available)
        ]


class ActionGetExhibitMatchIds(Action):
    def name(self) -> Text:
        return "action_get_exhibit_match_ids"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict) -> List[Dict[Text, Any]]:
        exhibit = tracker.get_slot("exhibit_alias")
        alias_matches = []
        if exhibit:
            alias_matches += get_exhibit_alias_matches(exhibit)
        match_ids = []
        for alias in alias_matches:
            match_ids += get_exhibit_ids(alias)
        match_ids = list(set(match_ids))
        matches_available = True if match_ids else False
        return [
            SlotSet("exhibit_id", None),
            SlotSet("num_tries", 0),
            SlotSet("exhibit_matches", match_ids),
            SlotSet("matches_available", matches_available)
        ]


class ActionGiveExplanation(Action):
    def name(self) -> Text:
        return "action_give_explanation"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict
            ) -> List[Dict[Text, Any]]:
        subject = tracker.get_slot("subject")
        article_matches = tracker.get_slot("article_matches")
        matches_available = tracker.get_slot("matches_available")
        num_tries = int(tracker.get_slot("num_tries"))
        if not subject:
            dispatcher.utter_message(response="utter_what_subject")
            return []
        if matches_available:
            [next_title, next_id] = article_matches[num_tries]
            explanation = get_article_text(article_id=next_id, title=next_title)
            if num_tries == 0:
                dispatcher.utter_message(response="utter_found_something")
            else:
                dispatcher.utter_message(response="utter_found_something_else")
            dispatcher.utter_message(text=explanation)
            num_tries += 1
            matches_available = (len(article_matches) > num_tries)
            return [
                SlotSet("subject", subject),
                SlotSet("num_tries", num_tries),
                SlotSet("matches_available", matches_available)
            ]
        else:
            dispatcher.utter_message(response="utter_found_nothing_else")
            return [
                SlotSet("subject", None),
                SlotSet("article_matches", []),
                SlotSet("num_tries", 0)
            ]


class ActionVerifyExhibit(Action):
    def name(self) -> Text:
        return "action_verify_exhibit"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict
            ) -> List[Dict[Text, Any]]:
        alias = tracker.get_slot("exhibit_alias")
        match_ids = tracker.get_slot("exhibit_matches")
        matches_available = tracker.get_slot("matches_available")
        num_tries = int(tracker.get_slot("num_tries"))
        if not alias:
            dispatcher.utter_message(response="utter_which_exhibit")
            return []
        if matches_available:
            exhibit_name = get_exhibit_name(match_ids[num_tries])
            msg = f"Are you referring to the exhibit called {exhibit_name}?"
            dispatcher.utter_message(text=msg)
            num_tries += 1
            matches_available = (len(match_ids) > num_tries)
            return [
                # SlotSet("exhibit_alias", alias),
                SlotSet("num_tries", num_tries),
                SlotSet("matches_available", matches_available)
            ]
        else:
            dispatcher.utter_message(response="utter_unknown_exhibit")
            return [
                SlotSet("exhibit_alias", None),
                SlotSet("exhibit_matches", []),
                SlotSet("num_tries", 0)
            ]


class ActionMapExhibitId(Action):
    def name(self) -> Text:
        return "action_map_exhibit_id"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[Dict[Text, Any]]:
        match_ids = tracker.get_slot("exhibit_matches")
        num_tries = tracker.get_slot("num_tries") - 1
        exhibit_id = match_ids[num_tries]
        return [SlotSet("exhibit_id", exhibit_id)]


class ActionUtterFaveExhibit(Action):
    def name(self) -> Text:
        return "action_utter_fave_exhibit"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict
            ) -> List[Dict[Text, Any]]:
        exhibit_id, exhibit_name, fun_fact = get_fave_exhibit()
        if fun_fact:
            fun_fact_alt = fun_fact[0].lower() + fun_fact[1:].rstrip(".")
            msgs = [
                f"One of my favorite exhibits at the Exploratorium is {exhibit_name}, because {fun_fact_alt}.",
                f"I like to recommend an exhibit called {exhibit_name}. {fun_fact}",
                f"One of the highlights of the Exploratorium is {exhibit_name}, since {fun_fact_alt}."
            ]
        else:
            msgs = [
                f"One of my favorite exhibits at the Exploratorium is {exhibit_name}.",
                f"I like to recommend an exhibit called {exhibit_name}.",
                f"One of the highlights of the Exploratorium is {exhibit_name}."
            ]
        msg = random.choice(msgs)
        dispatcher.utter_message(text=msg)
        return [SlotSet("exhibit_id", exhibit_id)]


class ActionUtterExhibitResponse(Action):
    def name(self) -> Text:
        return "action_utter_exhibit_response"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[Dict[Text, Any]]:
        exhibit_id = tracker.get_slot("exhibit_id")
        exhibit_name = get_exhibit_name(exhibit_id)
        events = list(reversed(tracker.events))
        user_msgs = [event for event in events if event["event"] == "user"]
        last_intents = [user_msgs[n]["parse_data"]["intent"]["name"] for n in range(len(user_msgs))]
        last_exhibit_intent = [intent for intent in last_intents if intent in exhibit_intents][0]
        if not exhibit_id:
            dispatcher.utter_message(response="utter_which_exhibit")
            return []
        elif last_exhibit_intent == "ask_where_exhibit":
            location, location_code = get_exhibit_location(exhibit_id)
            if location == "NOT ON VIEW":
                msg = f"{exhibit_name} is not currently on view."
            else:
                msg = f"{exhibit_name} is located in {location}."
            dispatcher.utter_message(text=msg)
            return[]
        elif last_exhibit_intent == "ask_about_exhibit":
            short_sum, medium_sum, fun_facts = get_about_exhibit(exhibit_id)
            if short_sum:
                dispatcher.utter_message(text=short_sum)
            elif medium_sum:
                dispatcher.utter_message(text=medium_sum)
            elif fun_facts:
                rand_fact = random.choice(fun_facts)
                dispatcher.utter_message(text=rand_fact)
            else:
                msg = f"I'm sorry, but I couldn't find any information about {exhibit_name}."
                dispatcher.utter_message(text=msg)
            return []
        elif last_exhibit_intent == "ask_exhibit_creator":
            creators = get_exhibit_creator(exhibit_id)
            if not creators:
                msg = f"I'm sorry, but I don't know who created {exhibit_name}."
                dispatcher.utter_message(text=msg)
            elif len(creators) == 1:
                msg = f"{exhibit_name} was created by {creators[0]}."
                dispatcher.utter_message(text=msg)
            elif len(creators) == 2:
                msg = f"{exhibit_name} was created by {creators[0]} and {creators[1]}."
                dispatcher.utter_message(text=msg)
            else:
                creators[-1] = "and " + creators[-1]
                creators = ", ".join(creators)
                msg = f"{exhibit_name} was created by {creators}."
                dispatcher.utter_message(text=msg)
            return []
        elif last_exhibit_intent == "ask_exhibit_date":
            year = get_exhibit_date(exhibit_id)
            if not year:
                msg = f"I'm sorry, but I'm not sure when {exhibit_name} was added as an exhibit."
                dispatcher.utter_message(text=msg)
            else:
                msg = f"{exhibit_name} became an exhibit in {year}."
                dispatcher.utter_message(text=msg)
            return []
        elif last_exhibit_intent == "ask_related_exhibit":
            related_ids = get_related_exhibit(exhibit_id)
            if not related_ids:
                msg = f"I'm sorry, but I'm not sure which exhibits are related to {exhibit_name}."
                dispatcher.utter_message(text=msg)
            else:
                related_id = random.choice(related_ids)
                related_name = get_exhibit_name(related_id)
                msg = f"{related_name} is an exhibit that is related to {exhibit_name}."
                dispatcher.utter_message(text=msg)
            return []
        else:
            msg = f"Please remind me of your question about {exhibit_name}."
            dispatcher.utter_message(text=msg)
            return []


class ActionResetSubject(Action):
    def name(self) -> Text:
        return "action_reset_subject"

    def run(self, dispatcher, tracker, domain) -> List[Dict[Text, Any]]:
        return [SlotSet("subject", None)]


class ActionResetExhibitAlias(Action):
    def name(self) -> Text:
        return "action_reset_exhibit_alias"

    def run(self, dispatcher, tracker, domain) -> List[Dict[Text, Any]]:
        return [SlotSet("exhibit_alias", None)]


class ActionResetExhibitId(Action):
    def name(self) -> Text:
        return "action_reset_exhibit_id"

    def run(self, dispatcher, tracker, domain) -> List[Dict[Text, Any]]:
        return [SlotSet("exhibit_id", None)]


class ActionResetExhibitSlots(Action):
    def name(self) -> Text:
        return "action_reset_exhibit_slots"

    def run(self, dispatcher, tracker, domain) -> List[Dict[Text, Any]]:
        return [
            SlotSet("exhibit_alias", None),
            SlotSet("exhibit_matches", []),
            SlotSet("matches_available", False),
            SlotSet("num_tries", 0)
        ]


class ActionResetExplanationSlots(Action):
    def name(self) -> Text:
        return "action_reset_explanation_slots"

    def run(self, dispatcher, tracker, domain) -> List[Dict[Text, Any]]:
        return [
            SlotSet("subject", None),
            SlotSet("article_matches", []),
            SlotSet("matches_available", False),
            SlotSet("num_tries", 0)
        ]
