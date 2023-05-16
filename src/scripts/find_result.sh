#!/bin/bash
# parse coverage.xml file and output a csv file

# Define the array of elements to search for
elements=(software.amazon.event.ruler.ACFinder software.amazon.event.ruler.ComparableNumber software.amazon.event.ruler.Patterns software.amazon.event.ruler.SingleStateNameMatcher software.amazon.event.ruler.Constants software.amazon.event.ruler.Field software.amazon.event.ruler.AnythingButEqualsIgnoreCase software.amazon.event.ruler.input.MultiByte software.amazon.event.ruler.input.InputByte software.amazon.event.ruler.input.InputWildcard software.amazon.event.ruler.input.DefaultParser software.amazon.event.ruler.input.ParseException software.amazon.event.ruler.input.InputMultiByteSet software.amazon.event.ruler.input.WildcardParser software.amazon.event.ruler.input.EqualsIgnoreCaseParser software.amazon.event.ruler.input.SuffixParser software.amazon.event.ruler.input.InputCharacter software.amazon.event.ruler.AnythingBut software.amazon.event.ruler.ArrayMembership software.amazon.event.ruler.Range software.amazon.event.ruler.Finder software.amazon.event.ruler.CIDR software.amazon.event.ruler.ValuePatterns software.amazon.event.ruler.IntIntMap software.amazon.event.ruler.Path)

# Define the path to the XML file to search in
xml_file=$1
csv_file=$2

for element in "${elements[@]}"
do
    line=$(grep -m 1 "<class name=\"$element\"" "$xml_file")
    if [ -n "$line" ]; then
        # Step 3: Extract line-rate and branch-rate and append to CSV file
        line_rate=$(echo "$line" | sed -n 's/.*line-rate="\([^"]*\)".*/\1/p')
        branch_rate=$(echo "$line" | sed -n 's/.*branch-rate="\([^"]*\)".*/\1/p')
        line_rate_float=$(echo "scale=2; $line_rate" | bc)
        branch_rate_float=$(echo "scale=2; $branch_rate" | bc)
        echo "$element,$line_rate_float,$branch_rate_float" >> "$csv_file"
    fi
done

