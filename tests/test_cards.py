from fastapi.testclient import TestClient
from lingominer.models.template import TemplateLang


def test_card_creation_flow(client: TestClient):
    # 1. 创建模板
    template_data = {"name": "Vocabulary Processing Flow", "lang": TemplateLang.EN}
    response = client.post("/templates", json=template_data)
    assert response.status_code == 200
    template = response.json()

    # 2. 添加生成步骤（对应algo.py中的各个Task）
    generations = [
        {  # 对应g1
            "name": "extract_target",
            "method": "completion",
            "prompt": "Giving a paragraph, extract the target word and the sentence. the target word is highlighted with @@, the sentence is the sentence containing the target word. the text is: '{{decorated_paragraph}}'",
            "inputs": [],
        },
        {  # 对应g2
            "name": "extract_lemma",
            "method": "completion",
            "prompt": "Extract the lemma of the word. The lemma is the base form of the word. The word is: '{{word}}'",
            "inputs": ["word"],
        },
        {  # 对应g3
            "name": "explain_word",
            "method": "completion",
            "prompt": "Explain the word in the sentence. tell me the pronunciation and the explanation of the word. the word is: '{{word}}' the sentence is: '{{sentence}}'",
            "inputs": ["lemma", "sentence"],
        },
        {  # 对应g4
            "name": "summarize",
            "method": "completion",
            "prompt": "Summarize the text. The text is: '{{paragraph}}'",
            "inputs": [],
        },
        {  # 对应g5
            "name": "simplify",
            "method": "completion",
            "prompt": "Simplify the sentence. The sentence is: '{{sentence}}'",
            "inputs": ["sentence"],
        },
    ]

    # 创建generations和对应的fields
    generation_outputs = [
        [  # g1的输出
            {
                "name": "word",
                "type": "text",
                "description": "The target word to be extracted",
            },
            {
                "name": "sentence",
                "type": "text",
                "description": "The sentence containing the target word",
            },
        ],
        [  # g2的输出
            {"name": "lemma", "type": "text", "description": "The lemma of the word"}
        ],
        [  # g3的输出
            {
                "name": "pronunciation",
                "type": "text",
                "description": "The pronunciation of the word",
            },
            {
                "name": "explanation",
                "type": "text",
                "description": "The explanation of the word",
            },
        ],
        [  # g4的输出
            {
                "name": "summary",
                "type": "text",
                "description": "The summary of the text",
            }
        ],
        [  # g5的输出
            {
                "name": "simple_sentence",
                "type": "text",
                "description": "The simplified sentence",
            }
        ],
    ]

    # 创建generations和对应的fields
    for gen_data, outputs in zip(generations, generation_outputs):
        # 创建generation
        response = client.post(
            f"/templates/{template['id']}/generations", json=gen_data
        )
        assert response.status_code == 200
        generation = response.json()

        # 为generation创建output fields
        for output_data in outputs:
            field_data = {
                "name": output_data["name"],
                "type": output_data["type"],
                "description": output_data["description"],
                "generation_id": generation["id"],
            }
            response = client.post(
                f"/templates/{template['id']}/fields", json=field_data
            )
            assert response.status_code == 200

    # 3. 创建卡片（对应algo.py中的main流程）
    test_text = "In addition to its rings, Saturn has 25 satellites that measure at least 6 miles (10 kilometers) in diameter, and several smaller satellites. The largest of Saturn’s satellites, Titan, has a diameter of about 3,200 miles—larger than the planets Mercury and Pluto. Titan is one of the few satellites in the solar system known to have an atmosphere. Its atmosphere consists largely of nitrogen. Many of Saturn’s satellites have large craters For example, Mimas has a crater that covers about one-third the diameter of the satellite."

    card_data = {
        "paragraph": test_text,
        "pos_start": 432,
        "pos_end": 439,
    }

    response = client.post(f"/cards?template_id={template['id']}", json=card_data)
    assert response.status_code == 200, response.text
    card = response.json()

    # 4. 验证处理结果
    content = card["content"]
    assert "word" in content
    assert content["word"] == "craters"
    assert "sentence" in content
    assert "craters" in content["sentence"]
    assert "lemma" in content
    assert "pronunciation" in content
    assert "explanation" in content
    assert "summary" in content
    assert "simple_sentence" in content
    assert "crater" in content["lemma"].lower()  # 验证词根提取
    assert len(content["summary"]) < len(test_text)  # 验证摘要比原文短
