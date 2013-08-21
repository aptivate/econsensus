from publicweb.tests.selenium.pages.base import Base
from selenium.webdriver.common.by import By

class DecisionDetail(Base):
    decision_title = "#decision_snippet_envelope .page_title"
    decision_form = "#decision_update_form"
    edit_decision_link = ".controls > .edit"
    desciption_field_id = "id_description"
    
    def __init__(self, driver, decision):
        self.driver = driver
        self.decision = decision
        decision_detail_url = "/".join([
            self.driver.live_server_url, "item", "detail", decision.id, ""])
        self.driver.get(decision_detail_url)
        if not self.is_element_present(By.ID, "decision_snippet_envelope"):
            assert False, "This isn't the decision detail page"
    
    def edit_decision(self):
        edit_link = self.driver.find_element_by_css_selector(
             self.edit_decision_link)
        edit_link.click()
        self._wait_for_element(self.desciption_field_id)
    
    def clear_text_field(self, field_name):
        self.driver.find_element_by_name(field_name).clear()
    
    def update_text_field(self, field_name, new_description):
        self.driver.find_element_by_name(field_name).send_keys(new_description)
    
    def _submit_changes(self, form, replacement):
        self.driver.find_element_by_css_selector(
            form + " input[value=\"Save\"]").click()
        self._wait_for_element(replacement, 
           "Check the data being submitted is valid")
    
    def _cancel_changes(self, form, replacement):
        self.driver.find_element_by_css_selector(
            self.decision_form + " input[value=\"Cancel\"]").click()
        
        self._wait_for_element(replacement)
        
    def cancel_decision_changes(self):
        self._cancel_changes(self.decision_form, self.decision_title)        
    
    def submit_decison_changes(self):
        self._submit_changes(self.decision_form, self.decision_title)
        