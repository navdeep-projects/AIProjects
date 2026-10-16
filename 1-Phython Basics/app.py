print("Hello, World!")
print(1+1)
print("Python Basics")

from typing import Literal

def check_loan(credit_score: int) -> Literal["approved", "rejected"]:
    if credit_score >= 700:
        return "approved"
    else:
        return "rejected"


print(check_loan(750))
print(check_loan(650))

## additional information (Metadata) about the variable. 
from typing import Annotated

def greet(
    name: Annotated[str, "User's name"]
):
    print(f"Hello {name}")

greet("Navdeep")


docs = [
    ["apple", "banana"],
    ["mango", "orange"],
    ["grape"]
]

result = [item for sublist in docs for item in sublist]

print(result)


result1 = []

for sublist in docs:
    for item in sublist:
        result1.append(item)

print(result1)


