## Idea 1:
Parse website, download all content and source such that we can host it locally using wget. Then send it in one query to llm and ask answer.

## Idea 2:
Make function for simple tasks like
- Getting html source from url.
- Downloading and transcribing specified audio file from url. (Transcribing is required as LLM models don't support audio as input modality.)
- Downloading a file from url. (Also get some metadata)
- Executing python code given requirements and source code. (We might need this
as for a task like, sum the first column of the attached CSV, and if there's a high chance that the file is very large, attaching it to the query can waste tokens, instead, asking the llm to give a program to execute would be better. Also some tasks that are expected of the model seems like it requires code execution. This has to be carefully managed as the code given first time might not execute, we might have to do some iterations by giving the model the traceback or error.)
- Submit answer by a POST request to a url in a predetermined format.

Once we have such functions, we can use Openai model's function/tool calling features in a loop (bound by time, number of api calls etc) to get answer. If no answer found before loop terminates, then give up. move to next question.

We need to send a very optimized prompt asking the model to batch tool calls so as to have the least to and fro between our endpoint and the model. The functions should also be defined with succinct description. We have to also ask the model to use executing python fucntion tool only when required and provide the requirements as a list and the python code also as a single line of syntactically correct code if possible to reduce tokens.The code also should be such that after execution it should store the answer in an OS environemt variable called TDS_ANSWER, traceback in TDS_TRACEBACK and execution status in TDS_EXEC_STATUS. Or just print the output, capture stdout and stderr.

[TODO] Handle retries of failed function calls. Somehow pass it the error too, so that it can correct itself.
[TODO] Test for images
[TODO] Add some emailing features to send the Task recived as an email.
[TODO] Secret should be taken as a deployment secret. 
[TODO] Github token also a deployment secret.
[TODO] Add instruction to say that, if the model feels this task is not feasible with the given set of tools, and after one trial, then submit a  dummy anser and move to next.
[TODO] Add a model to update the query given to orchestrator
[TODO] Need to tell model that only memory directory is where it can store and access files.
,
        {
            "type": "function",
            "function": {
                "name": "get_image_as_base64_url",
                "description": "Attaches the image from the given URL as a base64 encoded data URL string to the prompt",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "URL of the image to convert to a base64 encoded data URL string"
                        },
                    },
                    "required": ["url"],
                    "additionalProperties": False
                },
                "strict": True
            }
        }

