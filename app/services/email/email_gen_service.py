from app.services.email.profanity import input_check_agent, CheckingResponse, contains_profanity
from app.services.email.draft_creator import email_draft_generator, EmailDraft
from app.services.email.final_email import final_email_generator, FinalEmail
from app.services.email.style_config import EmailStyleConfig
from app.services.email.schemas import UserInput
from agents import Runner


async def check_profanity_sufficient(user_input: str) -> CheckingResponse:
  """Use the Input Data Checker to check profanity of input. Checks also if the data is sufficient to create email"""
  result = await Runner.run(input_check_agent, user_input)
  return result.final_output
  
async def generate_draft(checked_input: CheckingResponse):
  """Use the Email Draft Generator to generate email draft"""
  input = f'Input użytkownika: {checked_input.user_query}'
  draft = await Runner.run(email_draft_generator, input=input)
  return draft.final_output

async def generate_final_email(draft_and_query: EmailDraft, style: EmailStyleConfig) -> FinalEmail:
    updated_draft = draft_and_query.model_copy(update={"style": style})
    email = await Runner.run(final_email_generator, str(updated_draft))
    return email.final_output


async def generate_email(user_input: UserInput):
    email_info = user_input.email_info
    email_style = user_input.email_style
    
    # Input validation
    if contains_profanity(email_info):
        return FinalEmail(
          user_query=email_info,
          email_title='',
          output_MD="Nieopowiednia treść",
          validation_pass=False
          )
    validated_result = await check_profanity_sufficient(email_info)
    if not validated_result.validation_pass:
        return FinalEmail(
          user_query=validated_result.user_query,
          email_title='',
          output_MD=validated_result.output_MD,
          validation_pass=False
          )
     # genrating draft
    draft_email = await generate_draft(validated_result)
    
    # generating final draft with style
    final_email = await generate_final_email(draft_email, email_style)
    final_email.validation_pass = True
    
    return final_email
  
