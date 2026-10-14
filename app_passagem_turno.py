          # Alterado para o modelo padrão estável e captura do erro real
          MODELO_LITE = "gemini-2.5-flash"
          resposta = None

          for key in api_keys:
            try:
              client = genai.Client(api_key=key)
              resposta = client.models.generate_content(
                  model=MODELO_LITE, contents=[image_otimizada, prompt_ocr]
              )
              if resposta and resposta.text:
                break
            except Exception as e:
              # Exibe o erro técnico exato na tela para facilitar a correção
              st.error(f"Detalhe técnico do erro da API: {e}")
              continue
