from agent import chart_agent
import gradio as gr

multi_modal_chart_agent = gr.Interface(fn=chart_agent,
                    inputs=[gr.Image(label="Upload image", type="filepath"), 'text'],
                    outputs=['image'],
                    title="Multi Modal chat agent",
                    description="Multi Modal chat agent",
                    allow_flagging="never")

multi_modal_chart_agent.launch(debug=True, share=False, show_api=False, server_port=4000, server_name="0.0.0.0")