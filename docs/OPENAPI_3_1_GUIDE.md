# OpenAPI 3.1対応ガイド

## OpenAPI 3.1の新機能と改善点

GPTMAKERフレームワークでは、最新のOpenAPI 3.1仕様に完全対応しています。

### 🆕 OpenAPI 3.1の主要新機能

#### 1. JSON Schema 2020-12 完全対応
```json
{
  "openapi": "3.1.0",
  "jsonSchemaDialect": "https://json-schema.org/draft/2020-12/schema",
  "components": {
    "schemas": {
      "User": {
        "type": "object",
        "properties": {
          "age": {
            "type": "integer",
            "minimum": 0,
            "maximum": 150
          }
        }
      }
    }
  }
}
```

#### 2. 改善されたWebhooks サポート
```json
{
  "webhooks": {
    "eventName": {
      "post": {
        "summary": "イベント通知",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/Event"
              }
            }
          }
        }
      }
    }
  }
}
```

#### 3. oneOf/anyOf/allOf の改善
```json
{
  "schema": {
    "oneOf": [
      {
        "type": "string",
        "format": "email"
      },
      {
        "type": "string", 
        "format": "phone"
      }
    ]
  }
}
```

#### 4. より柔軟なコールバック定義
```json
{
  "callbacks": {
    "onComplete": {
      "{$request.body#/callbackUrl}": {
        "post": {
          "summary": "完了通知",
          "requestBody": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/Result"
                }
              }
            }
          }
        }
      }
    }
  }
}
```

### 📊 OpenAPI 3.0 vs 3.1 比較表

| 機能 | OpenAPI 3.0 | OpenAPI 3.1 | 改善点 |
|------|-------------|-------------|--------|
| JSON Schema | Draft 4 ベース | 2020-12 完全対応 | より柔軟な型定義 |
| Webhooks | 非対応 | ネイティブサポート | イベント駆動設計 |
| 型システム | 限定的 | 完全なJSON Schema | oneOf/anyOf改善 |
| ライセンス | 文字列のみ | SPDX識別子対応 | 標準化 |
| 例の定義 | 限定的 | より豊富 | テスト・文書化向上 |

### 🔧 GPTMAKERでのOpenAPI 3.1活用方法

#### 1. 高度なAction設定
```python
# chatgpt_deployer.py での自動設定
def _configure_actions(self, actions: list):
    """OpenAPI 3.1仕様の自動設定"""
    for action in actions:
        # OpenAPI 3.1の新機能を活用したスキーマ設定
        schema = action['schema']
        
        # JSON Schema Dialect指定
        if 'jsonSchemaDialect' not in schema:
            schema['jsonSchemaDialect'] = "https://json-schema.org/draft/2020-12/schema"
        
        # Webhooks設定
        if 'webhooks' in schema:
            self._configure_webhooks(schema['webhooks'])
```

#### 2. 複雑なデータ型の定義
```json
{
  "components": {
    "schemas": {
      "FlexibleData": {
        "oneOf": [
          {
            "type": "object",
            "properties": {
              "type": {"const": "user"},
              "data": {"$ref": "#/components/schemas/User"}
            }
          },
          {
            "type": "object", 
            "properties": {
              "type": {"const": "product"},
              "data": {"$ref": "#/components/schemas/Product"}
            }
          }
        ],
        "discriminator": {
          "propertyName": "type"
        }
      }
    }
  }
}
```

#### 3. 高度なバリデーション
```json
{
  "schema": {
    "type": "object",
    "properties": {
      "email": {
        "type": "string",
        "format": "email",
        "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
      },
      "age": {
        "type": "integer",
        "minimum": 0,
        "maximum": 150,
        "exclusiveMaximum": true
      }
    },
    "required": ["email"],
    "additionalProperties": false
  }
}
```

### 🚀 実装のベストプラクティス

#### 1. バージョン管理
```json
{
  "openapi": "3.1.0",
  "info": {
    "title": "My API",
    "version": "1.0.0",
    "description": "OpenAPI 3.1の新機能を活用したAPI"
  }
}
```

#### 2. セキュリティ強化
```json
{
  "components": {
    "securitySchemes": {
      "BearerAuth": {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT"
      },
      "OAuth2": {
        "type": "oauth2",
        "flows": {
          "authorizationCode": {
            "authorizationUrl": "https://example.com/auth",
            "tokenUrl": "https://example.com/token",
            "scopes": {
              "read": "読み取り権限",
              "write": "書き込み権限"
            }
          }
        }
      }
    }
  }
}
```

#### 3. エラーハンドリング
```json
{
  "responses": {
    "400": {
      "description": "バリデーションエラー",
      "content": {
        "application/json": {
          "schema": {
            "type": "object",
            "properties": {
              "errors": {
                "type": "array",
                "items": {
                  "type": "object",
                  "properties": {
                    "field": {"type": "string"},
                    "message": {"type": "string"},
                    "code": {"type": "string"}
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
```

### 📚 参考リンク

- [OpenAPI 3.1 Specification](https://spec.openapis.org/oas/v3.1.0)
- [JSON Schema 2020-12](https://json-schema.org/draft/2020-12/schema)
- [OpenAPI 3.0から3.1への移行ガイド](https://blog.stoplight.io/openapi-3-1)

### 🎯 次のステップ

1. 既存のAPI仕様をOpenAPI 3.1に更新
2. Webhooks機能の活用
3. より厳密な型定義の実装
4. 自動テストの強化
