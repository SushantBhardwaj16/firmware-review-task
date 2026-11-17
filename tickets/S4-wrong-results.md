# S4: Two wrong results in the engine

**Area:** Python. **Type:** fix. **Points:** 15. Optional.

## The report

From the analyst who reviewed the last report:

> Two of the components the engine lists for this image are wrong. One is a component that is not in the
> image at all. The other has the wrong version. Both led to findings in the report.

## What to do

1. Find the two wrong components and what in the engine causes each.
2. Fix each cause, so the same mistake cannot happen for other names and other images.
3. Add tests that fail on the code as you received it and pass on yours.
4. Say in your review report what the causes were.

## Done means

- `python3 -m minifw components work` lists neither wrong component.
- The engine reports a component only on evidence that it is installed: never from a file name that only
  resembles a known one, and never from what a document says.
- The fix is general. A fix that only knows about this image's file names does not count: our tests use
  another device.
- Everything that worked before still works.
