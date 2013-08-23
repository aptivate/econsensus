from publicweb.tests.selenium.pages.base import Base
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait

class DecisionDetail(Base):
    desciption_field_id = "#id_description"
    deadline_field = "#id_deadline"
    error_list = ".parsley-error-list > li"
    form_id = "#decision_update_form"
    edit_link_selector = ".controls > .edit"
    replaced_element = "#decision_snippet_envelope .page_title"
    
    def __init__(self, driver, decision):
        self.driver = driver
        self.decision = decision
        decision_detail_url = "/".join([
            self.driver.live_server_url, "item", "detail", str(decision.id), ""])
        self.driver.get(decision_detail_url)
        if not self.is_element_present(By.ID, "decision_snippet_envelope"):
            assert False, "This isn't the decision detail page"
    
    def _click_link(self, link, replacement=None):
        link_element = self.driver.find_element_by_css_selector(link)
        link_element.click()
        if replacement:
            self._wait_for_element(replacement)
    
    def clear_text_field(self, field_name):
        self.driver.find_element_by_name(field_name).clear()
    
    def update_text_field(self, field_name, new_value):
        self.driver.find_element_by_name(field_name).send_keys(new_value)
    
    def update_select_field(self, field_name, new_value):
        selector = Select(self.driver.find_element_by_name(field_name))
        selector.select_by_visible_text(new_value)
    
    def get_select_field_value(self, field_name):
        selector = Select(self.driver.find_element_by_name(field_name))
        return selector.all_selected_options[0].text
    
    def _submit_changes(self, form, replacement):
        self.driver.find_element_by_css_selector(
            form + " input[value=\"Save\"]").click()
        self._wait_for_element(replacement, 
           "Check the data being submitted is valid")
    
    def submit_invalid_changes(self, form):
        self.driver.find_element_by_css_selector(
            form + " input[value=\"Save\"]").click()
        self._wait_for_element(self.error_list)
        
    def _cancel_changes(self, form, replacement):
        self.driver.find_element_by_css_selector(
             form + " input[value=\"Cancel\"]").click()
        self._wait_for_element(replacement)               

    def cancel_changes(self):
        self._cancel_changes(self.form_id, self.replaced_element)        
    
    def submit_changes(self):
        self._submit_changes(self.form_id, self.replaced_element)
    
    def edit_decision(self):
        self._click_link(self.edit_link_selector, self.desciption_field_id)

class ActionitemDetail(DecisionDetail):
    form_id = ".actionitem-form"
    
    def cancel_changes(self):
        self._cancel_changes(self.form_id, self.edit_link_selector)
        
    def edit_decision(self):
        edit_link_selector = super(ActionitemDetail, self).edit_link_selector
        self._click_link(edit_link_selector, self.desciption_field_id)
        
class NewActionitemDetail(ActionitemDetail):
    edit_link_selector = "a.button.add_actionitem"
    replaced_element = "#actionitem_add_anchor"
     
    def add_actionitem(self):
        self._click_link(self.edit_link_selector, self.form_id)

class EditActionitemDetail(ActionitemDetail):
    edit_link_selector = ".edit.actionitem"
    replaced_element = ".actionitem_list > li > .actionitem_feedback_wrapper"
    
    def edit_actionitem(self):
        self._click_link(self.edit_link_selector, self.deadline_field)

class FeedbackDetail(DecisionDetail):
    form_id = "#feedback_add_anchor > form"
    feedback_type_selector = "#decision_detail .stats a dt.%s"
    feedback_type_count_path = ("//*[@id='decision_detail']//*[@class='stats']/"
                             "a/dt[@class='%s']/following-sibling::dd")
    
    def change_visibility(self, element):
        self._click_link(element)
    
    def _check_element_visibility(self, element, status, how=By.CSS_SELECTOR):
        if self.is_element_present(how=how, what=element):
            the_element = self.driver.find_element(by=how, value=element)
            return the_element.is_displayed() == status
        else:
            return False
    
    def add_feedback_of_type(self, feedback_type):
        self._click_link(
            self.feedback_type_selector % feedback_type, "#id_description")
    
    def get_number_of_feeback_type(self, feedback_type):
        feedback_type_count_path = self.feedback_type_count_path % feedback_type
        feedback_type_count = self.driver.find_element(
         by=By.XPATH, value=feedback_type_count_path).text
        return int(feedback_type_count)
    
    def is_element_visible(self, element, find_by=By.CSS_SELECTOR):
        return self._check_element_visibility(element, True, find_by)
    
    def is_element_hidden(self, element, find_by=By.CSS_SELECTOR):
        return self._check_element_visibility(element, False, find_by)

class NewFeedbackDetail(FeedbackDetail):
    edit_link_selector = "a.button.add_feedback"
    replaced_element = edit_link_selector
    
    def add_feedback_item(self):
        self._click_link(self.edit_link_selector, self.form_id)

class EditFeedbackDetail(FeedbackDetail):
    form_id = ".feedback_list > li > form"
    edit_link_selector = ".description .edit"
    replaced_element = ".feedback_type"
    
    def edit_feedback(self):
        self._click_link(self.edit_link_selector, self.form_id)

class CommentDetail(DecisionDetail):
    form_id = ".contrib_comment_container > .form_comment > form"
    edit_link_selector = ".show"
    replaced_element = edit_link_selector
    
    def is_element_displayed(self, how, what):
        try: 
            return self.driver.find_element(by=how, value=what).is_displayed()
        except NoSuchElementException: 
            return False
    
    def _submit_changes(self, form, replacement):
        self.driver.find_element_by_css_selector(
            form + " input[value=\"Post\"]").click()
        WebDriverWait(self.driver, 10).until(
            lambda x: not x.find_element_by_css_selector(form).is_displayed(),
            "Check that the form data is valid")
    
    def submit_invalid_changes(self, form):
        self.driver.find_element_by_css_selector(
            form + " input[value=\"Post\"]").click()
        self._wait_for_element(self.error_list)
                                   
    def add_comment(self):
        self._click_link(self.edit_link_selector, self.form_id)
    
    def click_outside_form(self):
        self._click_link('body')