# Review checklist

Compare the certificate with the root text and the analysis basis. Do not grade fluency. Do not add a reading that the basis does not support.

Answer each question. A material "no" is an objection.

1. Are the predicates in the root represented, and only those predicates?
2. Does every predicate have the subject, object, or other role the basis requires?
3. Are negation, modality, attribution, quantifiers, and other qualifiers attached to the propositions the basis requires?
4. Is a coordinator recorded as the operator it is: `and` as conjunction, `or` / `either` as disjunction, `if` as a condition?
5. If the basis gives more than one live reading, are all of them present and structurally distinct?
6. If the basis rejects a reading, is that reading absent from the live readings?
7. Does any proposition add a word that is not in the root, or add an event the basis does not support?
8. Does every source span reproduce the root slice it cites?
9. Does the ledger account for the words of the root without hiding a dropped role, operator, qualifier, or reading?
10. Does the top-level class match the live readings in the certificate?

A disclosed guideline application is consistent when the basis states it and the certificate follows it. Do not reject that disclosure as an invention. Do reject a certificate that omits a role, qualifier, operator, or live reading the basis requires, or that attaches one to the wrong proposition.

## Reading rules for the same questions

These rules say where to look. They do not add a question.

- Question 2 looks only at `predicates[].roles`. An obligation description, a proposition string, or a ledger row that mentions a subject or object does not create that role. If the basis requires the role and the `roles` array has no matching entry on that predicate, the answer is no. Use `REJECT_ROLE_BINDING`.
- Question 3 looks only at live `scope_bindings` and at obligations of the same kind whose `source_spans[].text` is the required token. A word left inside proposition text, or named only inside a description, is not a negation, modality, attribution, quantifier, or other qualifier. `ACCOUNTED_NON_MATERIAL` does not preserve a qualifier the basis requires. If the required binding is absent, the answer is no. Use `REJECT_OMISSION`. If the binding targets the wrong proposition, use `REJECT_SCOPE`.
- Question 3 also compares a `MODALITY` obligation description with the force the basis states. Necessity and permission are different forces. The modal word remaining in the root does not keep the stated force.
- Question 5 counts readings whose `status` is `MATERIALLY_LIVE`. If the basis names two live readings and only one remains, the answer is no. Use `REJECT_OMISSION`.
- Question 8 is string equality: `span.text` must equal `root.text[span.start:span.end]` for every predicate, role, binding, and obligation span. If any span fails, the answer is no. Use `REJECT_SOURCE_BINDING`. The ledger stores one row per word. A span that covers several words is exact when its text equals that slice. Do not answer no merely because the ledger splits those words.
- Question 9 is not satisfied by `completeness` booleans set to true or by an empty unassigned list. Those fields do not prove that a role, operator, qualifier, or live reading is present.

Verdicts:

- `ACCEPT_COMPLETE` when every answer is yes and there is no material objection.
- `REJECT_OMISSION` when a required predicate, role, qualifier, operator, or live reading is missing.
- `REJECT_INVENTION` when a proposition or obligation adds unsupported content.
- `REJECT_SCOPE` when a qualifier, quantifier, negation, modality, or attribution is attached to the wrong proposition.
- `REJECT_ROLE_BINDING` when a subject, object, or other required role is missing or assigned to the wrong predicate.
- `REJECT_OPERATOR` when conjunction, disjunction, or condition is mislabeled.
- `REJECT_SOURCE_BINDING` when a span does not reproduce the root.
- `INCONCLUSIVE_REVIEW` when the basis and the root do not determine the answer.

`ACCEPT_COMPLETE` requires an empty objection list.
